import zipfile
import xml.etree.ElementTree as ET
import sys
import os

def count_sheet_rows(filepath):
    print(f"Analyzing file: {filepath}")
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

    with zipfile.ZipFile(filepath, 'r') as z:
        # Parse sheet relation names
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

        print(f"{'Sheet Name':<25} | {'Total Rows (approx)':<20}")
        print("-" * 50)
        for name, xml_path in sheets:
            count = 0
            try:
                with z.open('xl/' + xml_path) as f:
                    context = ET.iterparse(f, events=('end',))
                    for event, elem in context:
                        if elem.tag.endswith('}row'):
                            count += 1
                            elem.clear()
            except Exception as e:
                count = f"Error: {e}"
            print(f"{name:<25} | {count:<20}")

if __name__ == "__main__":
    count_sheet_rows("Layer_1 4.xlsx")
