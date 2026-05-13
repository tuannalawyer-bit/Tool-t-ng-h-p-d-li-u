import zipfile
import xml.etree.ElementTree as ET
import sys
import os
import re
from collections import defaultdict

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

def get_cell_value(elem, cell_type, shared_strings):
    val_elem = elem.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
    if val_elem is None or val_elem.text is None:
        return None
    val = val_elem.text
    if cell_type == 's':
        try:
            idx = int(val)
            return shared_strings[idx] if idx < len(shared_strings) else f"SS_{idx}"
        except:
            return val
    return val

def parse_sheet_all_rows(z, xml_path, shared_strings):
    rows = []
    try:
        with z.open('xl/' + xml_path) as f:
            context = ET.iterparse(f, events=('start', 'end'))
            current_row_data = {}
            
            for event, elem in context:
                tag = elem.tag
                if event == 'start':
                    if tag.endswith('}row'):
                        current_row_data = {}
                elif event == 'end':
                    if tag.endswith('}c'):
                        cell_ref = elem.attrib.get('r')
                        cell_type = elem.attrib.get('t')
                        val = get_cell_value(elem, cell_type, shared_strings)
                        if val is not None and cell_ref:
                            # Extract column letter
                            col = re.sub(r'\d+', '', cell_ref)
                            current_row_data[col] = val
                    elif tag.endswith('}row'):
                        if current_row_data:
                            rows.append(current_row_data)
                        elem.clear()
    except Exception as e:
        print(f"Error parsing {xml_path}: {e}")
    return rows

def main():
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

    filepath = "Layer_1 4.xlsx"
    
    print("=== STARTING INVENTORY DEEP-DIVE ANALYSIS ===")
    with zipfile.ZipFile(filepath, 'r') as z:
        # Parse sheet mapping
        rel_map = {}
        with z.open('xl/_rels/workbook.xml.rels') as f:
            tree = ET.parse(f)
            root = tree.getroot()
            ns = {'r': 'http://schemas.openxmlformats.org/package/2006/relationships'}
            for rel in root.findall('.//r:Relationship', ns):
                rel_map[rel.attrib.get('Id')] = rel.attrib.get('Target')

        sheets = {}
        with z.open('xl/workbook.xml') as f:
            tree = ET.parse(f)
            root = tree.getroot()
            ns = {'ns': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
            for sheet in root.findall('.//ns:sheet', ns):
                sname = sheet.attrib.get('name')
                rid = sheet.attrib.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
                xml_path = rel_map.get(rid, "Unknown")
                sheets[sname] = xml_path

        shared_strings = load_shared_strings(z)
        
        # 1. Analyze Ton_cao
        print("\nAnalyzing 'Ton_cao'...")
        ton_cao_rows = parse_sheet_all_rows(z, sheets['Ton_cao'], shared_strings)
        
        ton_cao_by_store = defaultdict(lambda: {'count': 0, 'total_value': 0.0, 'items': []})
        for row in ton_cao_rows:
            # Search all cells in row for descriptive string
            desc = ""
            for cell_val in row.values():
                if 'tồn cuối =' in str(cell_val) and 'chưa bán =' in str(cell_val):
                    desc = str(cell_val)
                    break
            
            if desc:
                # Extract values using regex
                store_match = re.search(r'tại CH\s+([A-Za-z0-9]+)', desc)
                val_match = re.search(r'tồn cuối\s*=\s*(\d+)', desc)
                days_match = re.search(r'chưa bán\s*=\s*(\d+)', desc)
                
                store = store_match.group(1) if store_match else "Unknown"
                value = float(val_match.group(1)) if val_match else 0.0
                days = int(days_match.group(1)) if days_match else 0
                
                ton_cao_by_store[store]['count'] += 1
                ton_cao_by_store[store]['total_value'] += value
                ton_cao_by_store[store]['items'].append((value, days))
        
        # 2. Analyze CLKK_20%
        print("Analyzing 'CLKK_20%'...")
        clkk_rows = parse_sheet_all_rows(z, sheets['CLKK_20%'], shared_strings)
        clkk_by_store = defaultdict(lambda: {'count': 0, 'types': []})
        for row in clkk_rows:
            # Look for Store ID and Category. 
            # Based on earlier analysis, column K often has Store code/name, or column C/D.
            # Let's inspect descriptions
            desc = ""
            for cell_val in row.values():
                if 'Cảnh báo: Giá trị điều chỉnh' in str(cell_val) or 'Cảnh báo: Có điều chỉnh' in str(cell_val):
                    desc = str(cell_val)
                    break
            
            # Also, let's find any cell that looks like store ID/name
            store_name = ""
            for col, val in row.items():
                val_str = str(val)
                if val_str.startswith('WM+') or val_str.startswith('WIN') or val_str.startswith('[Block]'):
                    store_name = val_str
                    break
            
            if store_name or desc:
                key = store_name if store_name else "Unknown Store"
                clkk_by_store[key]['count'] += 1
                if desc:
                    clkk_by_store[key]['types'].append(desc)

        # 3. Analyze STO_Treo_>10tr
        print("Analyzing 'STO_Treo_>10tr'...")
        sto_rows = parse_sheet_all_rows(z, sheets['STO_Treo_>10tr'], shared_strings)
        sto_by_store = defaultdict(lambda: {'count': 0, 'total_value': 0.0})
        for row in sto_rows:
            # Typically Col A is Store ID, Col B is Store Name, Col L/M might be value.
            # Let's look for values above 10,000,000 in row
            store = row.get('A', 'Unknown')
            name = row.get('B', '')
            val = 0.0
            # Scan numerical values in the row to find the actual amount
            for v in row.values():
                try:
                    num = float(v)
                    if num >= 10000000 and num < 10000000000: # Range of millions to billions
                        val = max(val, num)
                except:
                    pass
            
            if store != 'Unknown' and val > 0:
                sto_by_store[store]['count'] += 1
                sto_by_store[store]['total_value'] += val
                sto_by_store[store]['name'] = name

        # --- REPORT GENERATION ---
        print("\n=============================================================")
        print("                  INVENTORY RISK AUDIT REPORT                ")
        print("=============================================================\n")
        
        # Part 1: Top Tồn Cao Không Bán
        print("1. TOP 10 STORES WITH HIGHEST AGING INVENTORY VALUE (Top 50 SKUs)")
        print("-" * 85)
        print(f"{'Store ID':<15} | {'Count of Top SKUs':<20} | {'Total Stuck Value (VND)':<25} | {'Max Days Stuck':<15}")
        print("-" * 85)
        sorted_ton_cao = sorted(ton_cao_by_store.items(), key=lambda x: x[1]['total_value'], reverse=True)
        for store, data in sorted_ton_cao[:10]:
            max_days = max([d for v, d in data['items']]) if data['items'] else 0
            val_str = f"{data['total_value']:,.0f} VND"
            print(f"{store:<15} | {data['count']:<20} | {val_str:<25} | {max_days:<15}")
            
        # Part 2: Top CLKK
        print("\n2. TOP 10 STORES WITH HIGHEST COUNT OF MAJOR INVENTORY VARIANCES (CLKK >= 20%)")
        print("-" * 85)
        print(f"{'Store / Location':<60} | {'Variance Occurrences':<20}")
        print("-" * 85)
        sorted_clkk = sorted(clkk_by_store.items(), key=lambda x: x[1]['count'], reverse=True)
        for store, data in sorted_clkk[:10]:
            if store != 'Unknown Store':
                print(f"{store[:58]:<60} | {data['count']:<20}")

        # Part 3: Top STO Treo
        print("\n3. TOP 10 STORES WITH HIGHEST PENDING STO VALUE (> 10M)")
        print("-" * 85)
        print(f"{'Store ID':<15} | {'Store Name':<40} | {'Pending Value (VND)':<25}")
        print("-" * 85)
        sorted_sto = sorted(sto_by_store.items(), key=lambda x: x[1]['total_value'], reverse=True)
        for store, data in sorted_sto[:10]:
            name = data.get('name', '')[:38]
            print(f"{store:<15} | {name:<40} | {data['total_value']:,.0f} VND")

if __name__ == "__main__":
    main()
