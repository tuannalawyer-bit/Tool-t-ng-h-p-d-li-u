import re
import json
import sys
import codecs

try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

def detect_and_read(path):
    # Try common powershell redirection encodings
    for enc in ['utf-16-le', 'utf-16', 'utf-8', 'cp1252']:
        try:
            with codecs.open(path, 'r', encoding=enc) as f:
                content = f.read()
                # If content looks valid
                if len(content) > 100 and 'VBA' in content:
                    print(f"Successfully read file using {enc}")
                    return content
        except Exception as e:
            continue
    return None

def analyze_vba_structure(file_path):
    content = detect_and_read(file_path)
    if not content:
        print("Could not read file with any known encoding.")
        return
        
    # Write a UTF-8 copy for easy future reading by view_file
    with open("vba_code_utf8.txt", "w", encoding="utf-8") as f:
        f.write(content)
    print("Saved a clean UTF-8 copy as vba_code_utf8.txt")
    
    # Split content by OLEVBA module separator, usually starts with '-----'
    # Let's find modules by 'VBA MACRO' or 'Attribute VB_Name'
    
    # Let's split by 'VBA MACRO'
    segments = re.split(r'={5,}', content)
    
    structure = []
    
    for seg in segments:
        # Look for macro name
        # Typically: "VBA MACRO Module1.bas"
        macro_match = re.search(r'VBA MACRO ([^\s]+)', seg)
        name_match = re.search(r'Attribute VB_Name = "([^"]+)"', seg)
        
        module_name = None
        if macro_match:
            module_name = macro_match.group(1)
        elif name_match:
            module_name = name_match.group(1)
            
        if not module_name:
            continue
            
        # Extract procedures
        subs = re.findall(r'^\s*(?:Public |Private |Static )?(Sub|Function)\s+(\w+)\s*\(', seg, re.IGNORECASE | re.MULTILINE)
        sub_list = [f"{t} {name}" for t, name in subs]
        
        # Detect key imports
        apis = re.findall(r'Declare\s+(?:Sub|Function)\s+(\w+)\s+Lib\s+"([^"]+)"', seg, re.IGNORECASE)
        api_list = [f"{name} (from {lib})" for name, lib in apis]
        
        # Detect patterns
        has_http = "XMLHTTP" in seg or "WinHttp" in seg
        has_sap = "sap" in seg.lower() or "SAPGUI" in seg
        
        structure.append({
            "module_name": module_name,
            "procedure_count": len(subs),
            "procedures": sub_list,
            "api_calls": api_list,
            "flags": {
                "http": has_http,
                "sap": has_sap
            },
            "size_chars": len(seg)
        })
        
    with open("vba_structure.json", "w", encoding="utf-8") as f:
        json.dump(structure, f, ensure_ascii=False, indent=2)
        
    print(f"Mapped {len(structure)} modules.")
    
    # Print a quick readable summary of modules to stdout
    for s in structure:
        print(f"\nModule: {s['module_name']}")
        print(f"  Procedures: {', '.join(s['procedures'][:8])}")
        if len(s['procedures']) > 8:
            print(f"  ... and {len(s['procedures'])-8} more")
        if s['flags']['sap']:
            print("  [!] Contains SAP integration code.")
        if s['flags']['http']:
            print("  [!] Contains Web/HTTP requests.")

if __name__ == "__main__":
    analyze_vba_structure("vba_code.txt")
