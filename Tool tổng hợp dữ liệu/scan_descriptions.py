import zipfile
import xml.etree.ElementTree as ET
import sys
import os
import re

def load_shared_strings(z):
    shared_strings = []
    try:
        with z.open('xl/sharedStrings.xml') as f:
            for event, elem in ET.iterparse(f, events=('end',)):
                if elem.tag.endswith('}si'):
                    text = "".join(elem.itertext())
                    shared_strings.append(text)
                    elem.clear()
    except KeyError:
        pass
    return shared_strings

def scan_sheet(z, xml_path, shared_strings, sheet_name):
    results = []
    try:
        with z.open('xl/' + xml_path) as f:
            context = ET.iterparse(f, events=('start', 'end'))
            current_row = None
            cell_type = None
            
            for event, elem in context:
                tag = elem.tag
                if event == 'start':
                    if tag.endswith('}row'):
                        current_row = int(elem.attrib.get('r', 1))
                        if current_row > 100: # Sample up to 100 rows
                            break
                    elif tag.endswith('}c'):
                        cell_type = elem.attrib.get('t')
                elif event == 'end':
                    if tag.endswith('}v'):
                        val = elem.text
                        if cell_type == 's' and val is not None:
                            try:
                                idx = int(val)
                                if idx < len(shared_strings):
                                    text = shared_strings[idx]
                                    # If text contains keywords indicating logic/risk, record it
                                    if any(kw in text.lower() for kw in ['rank', 'doanh thu', 'tồn cuối', 'triệu', 'chưa bán', 'nhóm', 'rủi ro', 'chênh lệch', 'lệch', 'đã bán', 'bán']):
                                        if text not in results:
                                            results.append(text)
                            except:
                                pass
                    elif tag.endswith('}row'):
                        elem.clear()
    except Exception as e:
        pass
    return results

def main():
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

    filepath = "Layer_1 4.xlsx"
    with zipfile.ZipFile(filepath, 'r') as z:
        # Parse relationship map
        rel_map = {}
        with z.open('xl/_rels/workbook.xml.rels') as f:
            tree = ET.parse(f)
            root = tree.getroot()
            ns = {'r': 'http://schemas.openxmlformats.org/package/2006/relationships'}
            for rel in root.findall('.//r:Relationship', ns):
                rel_map[rel.attrib.get('Id')] = rel.attrib.get('Target')

        # Parse sheets
        sheets = []
        with z.open('xl/workbook.xml') as f:
            tree = ET.parse(f)
            root = tree.getroot()
            ns = {'ns': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
            for sheet in root.findall('.//ns:sheet', ns):
                sname = sheet.attrib.get('name')
                rid = sheet.attrib.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
                xml_path = rel_map.get(rid, "Unknown")
                sheets.append((sname, xml_path))

        shared_strings = load_shared_strings(z)
        
        print("=== SCANNING EXPLANATORY STRINGS IN SHEETS ===")
        for name, xml_path in sheets:
            print(f"\n--- Sheet: {name} ---")
            texts = scan_sheet(z, xml_path, shared_strings, name)
            # Filter to unique and print first 10
            unique_texts = list(dict.fromkeys(texts))
            if not unique_texts:
                print("  No descriptive logic strings found in sample.")
            for i, t in enumerate(unique_texts[:15]):
                # truncate long strings for readability
                display = t if len(t) < 300 else t[:300] + "..."
                print(f"  [{i+1}] {display}")

if __name__ == "__main__":
    main()
