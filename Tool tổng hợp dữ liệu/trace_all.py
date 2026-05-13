import zipfile
import xml.etree.ElementTree as ET
import sys
import re

def load_shared_strings(z):
    shared_strings = []
    with z.open('xl/sharedStrings.xml') as f:
        for event, elem in ET.iterparse(f, events=('end',)):
            if elem.tag.endswith('}si'):
                text = "".join(elem.itertext())
                shared_strings.append(text)
                elem.clear()
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

def trace_all():
    sys.stdout.reconfigure(encoding='utf-8')
    filepath = "Layer_1 4.xlsx"
    with zipfile.ZipFile(filepath, 'r') as z:
        # Sheet Map
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
                sheets[sname] = rel_map.get(rid)

        shared_strings = load_shared_strings(z)
        xml_path = sheets['CLKK_20%']
        
        print("=== CLKK ROWS ===")
        with z.open('xl/' + xml_path) as f:
            context = ET.iterparse(f, events=('start', 'end'))
            current_row_idx = 0
            
            row_cells = {}
            for event, elem in context:
                tag = elem.tag
                if event == 'start':
                    if tag.endswith('}row'):
                        row_cells = {}
                        r_attr = elem.attrib.get('r')
                        if r_attr:
                            current_row_idx = int(r_attr)
                elif event == 'end':
                    if tag.endswith('}c'):
                        cell_ref = elem.attrib.get('r')
                        cell_type = elem.attrib.get('t')
                        val = get_cell_value(elem, cell_type, shared_strings)
                        if val is not None and cell_ref:
                            col = re.sub(r'\d+', '', cell_ref)
                            row_cells[col] = val
                    elif tag.endswith('}row'):
                        if current_row_idx <= 6:
                            print(f"\nROW {current_row_idx}:")
                            for col, v in sorted(row_cells.items()):
                                if col in ['A', 'B', 'C', 'D', 'L', 'M', 'AB', 'AC']:
                                    print(f"  {col}: {v}")
                        else:
                            break
                        elem.clear()

if __name__ == "__main__":
    trace_all()
