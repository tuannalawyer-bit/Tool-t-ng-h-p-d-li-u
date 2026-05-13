import zipfile
import xml.etree.ElementTree as ET
import sys
import os

def explore_xlsx(filepath):
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return

    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return

    print(f"Exploring: {filepath}")
    with zipfile.ZipFile(filepath, 'r') as z:
        # List size of key files
        print("\nKey file sizes:")
        for info in z.infolist():
            if 'sharedStrings' in info.filename or 'worksheets/' in info.filename or 'workbook.xml' in info.filename:
                print(f" - {info.filename}: {round(info.file_size / (1024*1024), 2)} MB ({info.file_size} bytes)")

        # Parse relationship map
        rel_map = {}
        try:
            with z.open('xl/_rels/workbook.xml.rels') as f:
                tree = ET.parse(f)
                root = tree.getroot()
                ns = {'r': 'http://schemas.openxmlformats.org/package/2006/relationships'}
                for rel in root.findall('.//r:Relationship', ns):
                    rel_map[rel.attrib.get('Id')] = rel.attrib.get('Target')
        except Exception as e:
            print(f"Error reading workbook rels: {e}")

        # Parse workbook to get sheet names
        try:
            with z.open('xl/workbook.xml') as f:
                tree = ET.parse(f)
                root = tree.getroot()
                # Namespaces in excel XML
                ns = {'ns': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
                sheets = root.findall('.//ns:sheet', ns)
                print("\nSheets found:")
                for sheet in sheets:
                    sname = sheet.attrib.get('name')
                    sid = sheet.attrib.get('sheetId')
                    rid = sheet.attrib.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
                    xml_path = rel_map.get(rid, "Unknown")
                    print(f" - Name: {sname}, SheetId: {sid}, Target: {xml_path}")
        except Exception as e:
            print(f"Error reading workbook.xml: {e}")


if __name__ == "__main__":
    explore_xlsx("Layer_1 4.xlsx")
