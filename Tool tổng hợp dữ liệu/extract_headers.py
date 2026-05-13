import zipfile
import xml.etree.ElementTree as ET
import sys
import os
import re

def load_shared_strings(z):
    print("Loading shared strings...")
    shared_strings = []
    try:
        with z.open('xl/sharedStrings.xml') as f:
            for event, elem in ET.iterparse(f, events=('end',)):
                if elem.tag.endswith('}t'):
                    # In excel shared strings, the text can be directly in <t> or split in <r><t>
                    # So we get all text in the element
                    shared_strings.append(elem.text if elem.text else "")
                elif elem.tag.endswith('}si'):
                    # To be safer, we can aggregate text under <si>
                    # Join all <t> contents inside <si>
                    text = "".join(elem.itertext())
                    shared_strings.append(text)
                    elem.clear() # clear memory
    except KeyError:
        print("No shared strings file.")
    print(f"Loaded {len(shared_strings)} shared strings.")
    return shared_strings

def parse_sheet_headers(z, xml_path, shared_strings):
    print(f"Reading {xml_path} headers...")
    rows = {}
    try:
        with z.open('xl/' + xml_path) as f:
            # We use iterparse to stream through the XML
            context = ET.iterparse(f, events=('start', 'end'))
            
            current_row = None
            current_cell = None
            cell_type = None
            formula = None
            value = None
            
            for event, elem in context:
                tag = elem.tag
                if event == 'start':
                    if tag.endswith('}row'):
                        current_row = int(elem.attrib.get('r', 1))
                        if current_row > 5: # Only read first 5 rows
                            break
                        rows[current_row] = {}
                    elif tag.endswith('}c'):
                        current_cell = elem.attrib.get('r')
                        cell_type = elem.attrib.get('t')
                        formula = None
                        value = None
                elif event == 'end':
                    if tag.endswith('}f'):
                        formula = elem.text
                    elif tag.endswith('}v'):
                        val = elem.text
                        if cell_type == 's' and val is not None:
                            try:
                                idx = int(val)
                                if idx < len(shared_strings):
                                    value = shared_strings[idx]
                                else:
                                    value = f"SS_IDX_{idx}"
                            except:
                                value = val
                        else:
                            value = val
                    elif tag.endswith('}c'):
                        if current_row in rows and current_cell:
                            rows[current_row][current_cell] = {
                                'val': value,
                                'formula': formula
                            }
                    elif tag.endswith('}row'):
                        elem.clear() # Free memory
    except Exception as e:
        print(f"Error parsing {xml_path}: {e}")
    return rows

def main():
    filepath = "Layer_1 4.xlsx"
    output_file = "headers.txt"
    
    with open(output_file, "w", encoding="utf-8") as out_f:
        def log(msg):
            out_f.write(msg + "\n")
            print(msg)

        with zipfile.ZipFile(filepath, 'r') as z:
            # Parse relationship map
            rel_map = {}
            with z.open('xl/_rels/workbook.xml.rels') as f:
                tree = ET.parse(f)
                root = tree.getroot()
                ns = {'r': 'http://schemas.openxmlformats.org/package/2006/relationships'}
                for rel in root.findall('.//r:Relationship', ns):
                    rel_map[rel.attrib.get('Id')] = rel.attrib.get('Target')

            # Parse workbook to get sheet names
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

            # Load shared strings
            shared_strings = load_shared_strings(z)

            # For each sheet, get the first 5 rows
            for name, xml_path in sheets:
                log(f"\n==================== Sheet: {name} ====================")
                rows = parse_sheet_headers(z, xml_path, shared_strings)
                for row_idx in sorted(rows.keys()):
                    log(f"Row {row_idx}:")
                    row_data = rows[row_idx]
                    # Print non-empty cells sorted by cell reference
                    sorted_cells = sorted(row_data.keys(), key=lambda x: (len(x), x)) # quick and dirty sort
                    for cell_ref in sorted_cells:
                        info = row_data[cell_ref]
                        val = info['val']
                        form = info['formula']
                        if val or form:
                            output = f"  {cell_ref}: "
                            if val is not None:
                                output += f"'{val}'"
                            if form is not None:
                                output += f" [FORMULA: {form}]"
                            log(output)

if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass
    main()

