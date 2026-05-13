import os, re, json, datetime
from bs4 import BeautifulSoup

# Init EasyOCR locally to avoid reloading
_reader = None
def get_ocr():
    global _reader
    if not _reader:
        import easyocr
        _reader = easyocr.Reader(['vi', 'en'], gpu=False)
    return _reader

REQUIRED_FIELDS = ['thang', 'ngay_nhan', 'ngay_tra', 'ma_mb', 'tinh_trang', 'thong_tin_mb', 'tinh', 'dtt', 'gia_thue_vat', 'bct', 'cv_tkmb', 'tn_tkmb']

FOLDER = r"D:\TĐMB\chạy tool"
EXCEL_NAME = "form tool.xlsx"
SHEET_NAME = "01. Thẩm định giá & HSPL"
DATA_START_ROW = 4
GEMINI_AVAILABLE = False

PROVINCE_MAP = {
    'MB': 'Hà Nội', 'MN': 'Hồ Chí Minh', 'HPG': 'Hải Phòng', 'BNH': 'Bắc Ninh',
    'YBI': 'Yên Bái', 'PTO': 'Phú Thọ', 'SLA': 'Sơn La', 'HYN': 'Hưng Yên', 'NAN': 'Nghệ An'
}

def init_gemini(api_key):
    pass  # Không dùng Gemini nữa

def detect_tinh_trang(subject):
    s = subject.lower()
    if 'hủy' in s: return 'Hủy'
    if 'tạm dừng' in s: return 'Tạm dừng'
    return 'Done'

def extract_cv_tkmb(sender_str):
    m = re.match(r'^"?([^"<]+)', str(sender_str))
    if m:
        name = m.group(1).strip()
        name = re.sub(r'\(.*?\)', '', name).strip()
        return name
    return str(sender_str)

def _clean_dtt(raw_dtt):
    s = str(raw_dtt).strip()
    if re.search(r'[Tt]\d|[Tt]rệt|tầng', s, re.IGNORECASE):
        nums = re.findall(r'(\d+(?:[.,]\d+)?)', s)
        if nums:
            total = sum(float(n.replace(',', '.')) for n in nums)
            return str(total) if total != int(total) else str(int(total))
    s = re.sub(r'\s*m2.*$', '', s, flags=re.IGNORECASE).strip()
    return s

def _validate_gia_thue(val):
    s = str(val).strip()
    if not s: return ''
    if 'http' in s.lower() or 'youtube' in s.lower(): return ''
    if any(kw in s.lower() for kw in ['thông tin quy hoạch', 'thẩm định', 'kstt', 'phản hồi']): return ''
    if 'link video' in s.lower(): return ''
    if len(s) > 20 and re.search(r'[a-zA-ZÀ-ỹ]', s): return ''
    clean = re.sub(r'(VND|vnđ|đ|\s)', '', s, flags=re.IGNORECASE)
    if re.search(r'[a-zA-ZÀ-ỹ]', clean): return ''
    return s

def extract_table_from_html(html_bytes):
    if not html_bytes: return {}
    try:
        soup = BeautifulSoup(html_bytes.decode('utf-8', errors='ignore'), 'lxml')
    except:
        return {}
    data = {}
    for table in soup.find_all('table'):
        rows = table.find_all('tr')
        if not rows: continue
        for i, row in enumerate(rows):
            cells = [c.get_text(separator=' ', strip=True) for c in row.find_all(['th', 'td'])]
            if not cells: continue
            if len(cells) == 2:
                data[cells[0].lower()] = cells[1]
            if any('mã mb' in c.lower() or 'giá thuê' in c.lower() or 'dtt' in c.lower() or 'diện tích' in c.lower() for c in cells):
                headers = [c.lower() for c in cells]
                if i + 1 < len(rows):
                    data_cells = [c.get_text(separator=' ', strip=True) for c in rows[i+1].find_all(['th', 'td'])]
                    for h, v in zip(headers, data_cells + ['']*(len(headers)-len(data_cells))):
                        if h and v: data[h] = v
    return data

def process_msg_file(msg_path, log_callback=None):
    import extract_msg
    result = {"success": False, "data": None, "error": "", "path": msg_path, "file": os.path.basename(msg_path)}
    try:
        msg = extract_msg.Message(msg_path)
        subject = str(msg.subject or "")
        body = str(msg.body or "")
        html_body = msg.htmlBody
        
        orig_date = msg.date
        if orig_date and orig_date.tzinfo:
            orig_date = orig_date.replace(tzinfo=None)
            
        reply_date = None
        if orig_date: reply_date = orig_date + datetime.timedelta(days=2)
        cv_sender = msg.sender or ""
        if subject.lower().startswith("re:"):
            m = re.search(r'From:\s+([^\n<]+)', body)
            if m: cv_sender = m.group(1).strip()
        
        # 1. HTML Parsing cho Text Emails
        table_data = extract_table_from_html(html_body)
        
        # Map fields
        ma_mb = table_data.get('mã mb', '') or table_data.get('mã trạm', '')
        ten_mb = table_data.get('tên mb', '') or table_data.get('tên mặt bằng', '')
        tinh = table_data.get('tỉnh', '') or table_data.get('tỉnh/thành phố', '')
        dtt = table_data.get('dtt (m2)', '') or table_data.get('dtt', '') or table_data.get('diện tích', '') or table_data.get('diện tích (m2)', '')
        gia_thue = table_data.get('giá thuê', '') or table_data.get('giá thuê có vat', '') or table_data.get('giá thuê có thuế', '')
        bct = table_data.get('thông tin bct', '') or table_data.get('bct', '')
        truong_nhom = table_data.get('trưởng nhóm', '') or table_data.get('trưởng nhóm phụ trách', '') or table_data.get('tn phụ trách', '')
        
        # 2. Regex Fallbacks (từ Subject và Body text)
        if not ma_mb:
            m = re.search(r'\b(MB[\s_]*\d+|MN[\s_]*\d+)', subject, re.IGNORECASE)
            if m: ma_mb = re.sub(r'[\s_]+', '', m.group(1)).upper()
            else:
                m2 = re.search(r'\((MB[^)]+|MN[^)]+)\)\s*$', subject)
                if m2: ma_mb = m2.group(1).strip()
        
        if ma_mb and not ten_mb:
            m = re.search(r'(?:MB:\s*|Mặt bằng\s*mở\s*mới[:\-\s]*(?:MB)?\s*|[-_]\s*)(' + re.escape(ma_mb) + r')\s*[-_:]*\s*([^(\n]+)', subject, re.IGNORECASE)
            if m:
                code = m.group(1).upper()
                name_part = re.sub(r'[-,\s_]+$', '', m.group(2).strip())
                ten_mb = 'WM+ ' + code + ' ' + name_part
                tinh = 'T. ' + PROVINCE_MAP.get(code[:2], code[:2])
                
        dtt = _clean_dtt(dtt)
        if not dtt or len(str(dtt)) > 20:
            m = re.search(r'(?:diện tích\s*(?:là\s*|:\s*)?|DTT[^\d\n]*)(\d+(?:[.,]\d+)?)|(\d+(?:[.,]\d+)?)\s*m2', body, re.IGNORECASE)
            if m: dtt = (m.group(1) or m.group(2)).replace(',', '.')
            
        gia_thue = _validate_gia_thue(gia_thue)
        if not gia_thue:
            prices = re.findall(r'(?<!\d)([1-9]\d{0,2}(?:[.,]\d{3}){2,})(?!\d)', body)
            if prices: gia_thue = _validate_gia_thue(prices[-1].replace(',', '.'))
            
        if not bct:
            body_phones = re.finditer(r'(?:Cô|Chú|Bác|Anh|Chị|Ông|Bà|BCT)\s*([A-Z][a-zà-ỹA-ZÀ-Ỹ\s]{1,20})?[:\-]?\s*(0\d{2,3}[\s.]?\d{3,4}[\s.]?\d{3,4})', body, re.IGNORECASE)
            for match in body_phones:
                name = match.group(1)
                n = name.strip() if name else 'BCT'
                bct = f'{n}: {match.group(2)}'; break
                
        if not ten_mb:
            m = re.search(r'(?:MB_?\s*|MBMM_\s*|MB:\s*)(.*?)\s*(?:\(MB\d|\(MN\d)', subject, re.IGNORECASE)
            if m: ten_mb = m.group(1).strip()
            
        if not ten_mb:
            m = re.search(r'WM\+\s+([A-Z]{3})\s+([^()]+)', subject, re.IGNORECASE)
            if m:
                code = m.group(1).upper()
                name_part = re.sub(r'[-,\s_]+$', '', m.group(2).strip())
                ten_mb = 'WM+ ' + code + ' ' + name_part
                if not tinh: tinh = PROVINCE_MAP.get(code, code)

        if not truong_nhom:
            m_tn = re.search(r'(?:Trưởng nhóm|TN(?: TKMB)?(?: phụ trách)?)\s*[:\-]\s*([A-Z][a-zà-ỹA-ZÀ-Ỹ\s]{2,30})', body, re.IGNORECASE)
            if m_tn: truong_nhom = m_tn.group(1).strip()
            
        # 3. NẾU VẪN THIẾU THÔNG TIN -> XỬ LÝ ẢNH BẰNG EASYOCR
        missing = not ma_mb or not dtt or not gia_thue or not bct
        if missing and msg.attachments:
            if log_callback: log_callback("📷 Dữ liệu thiếu, đang kích hoạt EasyOCR đọc ảnh...", "warn")
            ocr_text = ""
            for a in msg.attachments:
                fname = a.longFilename or a.shortFilename or ''
                if fname.lower().endswith(('.png', '.jpg', '.jpeg')) and a.data:
                    try:
                        import cv2
                        import numpy as np
                        img_array = np.frombuffer(a.data, np.uint8)
                        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                        reader = get_ocr()
                        res = reader.readtext(img, detail=0)
                        ocr_text += " ".join(res) + " \n"
                    except Exception as e:
                        if log_callback: log_callback(f"Lỗi đọc ảnh {fname}: {e}", "err")
            
            if ocr_text:
                ocr_text = ocr_text.replace('O', '0') # Fix O vs 0 in OCR
                if not ma_mb:
                    m = re.search(r'(MB\w*?\d+|MN\w*?\d+)', ocr_text, re.IGNORECASE)
                    if m: ma_mb = m.group(1).upper()
                if not gia_thue:
                    prices = re.findall(r'(?<!\d)([1-9]\d{0,2}(?:[.,]\d{3}){2,})(?!\d)', ocr_text)
                    if prices: gia_thue = _validate_gia_thue(prices[-1].replace(',', '.'))
                if not dtt:
                    m = re.search(r'(?:dtt|diện tích).*?(\d+(?:[.,]\d+)?)', ocr_text.lower())
                    if m: dtt = m.group(1)
                    else:
                        nums = re.findall(r'\b(\d{2,3})\b', ocr_text)
                        if nums: dtt = nums[0]
                if not bct:
                    b_match = re.search(r'(?:Cô|Chú|Bác|Anh|Chị|Ông|Bà|BCT)\s*([A-Z][a-zà-ỹA-ZÀ-Ỹ\s]{1,20})?[:\-]?\s*(0\d{2,3}[\s.]?\d{3,4}[\s.]?\d{3,4})', ocr_text, re.IGNORECASE)
                    if b_match:
                        n = b_match.group(1).strip() if b_match.group(1) else 'BCT'
                        bct = f'{n}: {b_match.group(2)}'
                if not truong_nhom:
                    m_tn = re.search(r'(?:Trưởng nhóm|TN(?: TKMB)?(?: phụ trách)?)\s*[:\-]\s*([A-Z][a-zà-ỹA-ZÀ-Ỹ\s]{2,30})', ocr_text, re.IGNORECASE)
                    if m_tn: truong_nhom = m_tn.group(1).strip()
                    else:
                        if "trưởng nhóm" in ocr_text.lower() or "tn:" in ocr_text.lower() or "tn :" in ocr_text.lower():
                            names = re.findall(r'(?<![a-z])(?:Nguyễn|Trần|Lê|Phạm|Hoàng|Huỳnh|Phan|Vũ|Võ|Đặng|Bùi|Đỗ|Hồ|Ngô|Dương|Lý)\s+[A-Z][a-zà-ỹA-ZÀ-Ỹ\s]{1,20}', ocr_text)
                            if names:
                                valid_names = [n for n in names if n not in str(bct)]
                                if valid_names: truong_nhom = valid_names[-1].strip()

        # Cleanups
        if truong_nhom and re.search(r'VND|tháng|\d{7,}|\(con gái|Nguyễn Thị Thanh|Thuỳ Dương|Lệ Quyên|Mỹ Hương', truong_nhom, re.IGNORECASE):
            truong_nhom = ''
        if ma_mb and any(kw in ma_mb.lower() for kw in ['thông tin', 'giá thuê', 'diện tích', 'dtt']): ma_mb = ''
        if dtt and re.search(r'[()]|^0\d{8,}', str(dtt)): dtt = ''
        if bct and re.match(r'^[\d.,\s]+$', bct.strip()): bct = ''
        if bct: bct = ' '.join(bct.split())
        if tinh:
            tinh = re.sub(r'^(?:T\.|Tỉnh|TP\.|Thành phố)\s+', '', tinh, flags=re.IGNORECASE).strip()

        kstt_text = ""
        try:
            kstt_idx = body.lower().find("kstt phản hồi")
            if kstt_idx == -1: kstt_idx = body.lower().find("thẩm định an ninh")
            if kstt_idx != -1:
                kstt_text = body[kstt_idx:kstt_idx+1000].strip()
                kstt_text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', kstt_text)
        except: pass

        def summarize_gia_thue(kstt):
            if not kstt: return ""
            if "giá thuê chưa bất thường" in kstt.lower() or "tntm đạt" in kstt.lower(): return "Giá thuê chưa bất thường, TNTM đạt"
            return ""

        def summarize_hspl(kstt):
            if not kstt: return ""
            if "đối chiếu định vị mặt bằng" in kstt.lower(): return "HSPL đầy đủ theo quy hoạch"
            return ""

        data = {
            "thang": orig_date.month if orig_date else "",
            "ngay_nhan": orig_date if orig_date else "",
            "ngay_tra": reply_date if reply_date else "",
            "ma_mb": ma_mb, "tinh_trang": detect_tinh_trang(subject),
            "thong_tin_mb": ten_mb, "tinh": tinh, "dtt": dtt,
            "gia_thue_vat": gia_thue, "bct": bct,
            "cv_tkmb": extract_cv_tkmb(cv_sender), "tn_tkmb": truong_nhom,
            "chi_tiet_thamdinh": kstt_text,
            "gia_thue_sum": summarize_gia_thue(kstt_text),
            "hspl": summarize_hspl(kstt_text),
            "ghi_chu": "",
        }
        
        for k, v in data.items():
            if isinstance(v, str):
                data[k] = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', v)

        final_missing = [f for f in REQUIRED_FIELDS if not str(data.get(f, "")).strip()]

        result["data"] = data
        result["missing_fields"] = final_missing

        if not final_missing:
            result["success"] = True
            if log_callback: log_callback("✅ Thành công: Đã trích xuất đầy đủ 100% các trường.", "ok")
        else:
            if data.get("ma_mb"):
                result["success"] = True
                result["partial"] = True
                if log_callback: log_callback(f"⚠️ Cảnh báo: Thiếu dữ liệu ({', '.join(final_missing)})", "warn")
            else:
                result["success"] = False
                result["error"] = "Không tìm thấy Mã mặt bằng"
                if log_callback: log_callback("❌ Lỗi: Không tìm thấy Mã mặt bằng", "error")

        return result
    except Exception as e:
        import traceback
        result["success"] = False
        result["error"] = f"Lỗi xử lý file: {str(e)}"
        if log_callback: log_callback(f"❌ Exception: {str(e)}\n{traceback.format_exc()}", "error")
        return result
