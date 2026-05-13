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

REQUIRED_FIELDS = ['thang', 'ngay_nhan', 'ngay_tra', 'ma_mb', 'tinh_trang', 'thong_tin_mb', 'tinh', 'dtt', 'gia_thue_vat', 'bct', 'cv_tkmb']

# Lấy đường dẫn của thư mục chứa file script này tự động
FOLDER = os.path.dirname(os.path.abspath(__file__))
EXCEL_NAME = "form tool.xlsx"
SHEET_NAME = "01. Thẩm định giá & HSPL"
DATA_START_ROW = 4
GEMINI_AVAILABLE = False

PROVINCE_MAP = {
    'MB': 'Hà Nội', 'MN': 'Hồ Chí Minh', 'HPG': 'Hải Phòng', 'BNH': 'Bắc Ninh',
    'YBI': 'Yên Bái', 'PTO': 'Phú Thọ', 'SLA': 'Sơn La', 'HYN': 'Hưng Yên', 'NAN': 'Nghệ An'
}

_gemini_client = None
try:
    import google.genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

def init_gemini(api_key):
    global _gemini_client, GEMINI_AVAILABLE
    try:
        from google import genai
        _gemini_client = genai.Client(api_key=api_key)
        GEMINI_AVAILABLE = True
    except Exception as e:
        GEMINI_AVAILABLE = False
        raise e

def detect_tinh_trang(subject, table_data=None):
    s = subject.lower()
    if 'hủy' in s: return 'Hủy'
    if 'tạm dừng' in s: return 'Tạm dừng'
    
    is_gia_han = 'gia hạn' in s
    if table_data and not is_gia_han:
        # Inspect table headers for evidence of renewal
        for k in table_data.keys():
            k_low = str(k).lower()
            if 'gia hạn' in k_low or 'mã site' in k_low or 'giá thuê gh' in k_low:
                is_gia_han = True
                break
                
    return 'Gia hạn' if is_gia_han else 'Mở mới'

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

def safe_fix_font(text):
    """Tự động chữa lỗi font do mã hóa CP1258/Latin1 bị hiểu sai, bảo toàn Unicode chuẩn."""
    if not isinstance(text, str) or not text: return text
    # Các dấu hiệu đặc trưng của mã hóa lỗi legacy Việt Nam hiển thị nhầm Latin-1
    bad_symbols = ['ý', 'õ', 'ò', 'Þ', 'Ì', 'Ð', 'ã'] 
    # Dùng any() check nhanh
    if any(sym in text for sym in ['ýõ', 'ò', 'Þ', 'Ì']):
        try:
            # Chuyển đổi ngược: Mã hóa latin1 thô và giải mã lại qua font VN gốc CP1258
            fixed = text.encode('latin1').decode('cp1258')
            return fixed
        except:
            return text
    return text

def extract_table_from_html(html_bytes, anchor_ma_mb=""):
    if not html_bytes: return {}
    try:
        try:
            soup = BeautifulSoup(html_bytes.decode('utf-8', errors='ignore'), 'lxml')
        except:
            # Fallback built-in html parser if lxml missing
            soup = BeautifulSoup(html_bytes.decode('utf-8', errors='ignore'), 'html.parser')
    except:
        return {}
    data = {}
    anchor_clean = str(anchor_ma_mb).strip().upper()
    
    for table in soup.find_all('table'):
        rows = table.find_all('tr')
        if not rows: continue
        for i, row in enumerate(rows):
            cells = [c.get_text(separator=' ', strip=True) for c in row.find_all(['th', 'td'])]
            if not cells: continue
            # 2-column simple vertical layout
            if len(cells) == 2:
                key = cells[0].lower().strip()
                val = cells[1].strip()
                # Only set if not exists OR if this row explicitly contains anchor
                if not data.get(key) or (anchor_clean and anchor_clean in val.upper()):
                    data[key] = val
            
            # Horizontal table layout with headers
            if any(any(kw in c.lower() for kw in ['mã mb', 'giá thuê', 'dtt', 'diện tích', 'mã site', 'tên ch']) for c in cells):
                headers = [c.lower().strip() for c in cells]
                # Scan all subsequent rows looking for the BEST row (the one matching anchor)
                best_row_data = {}
                found_target_row = False
                
                for data_row_idx in range(i + 1, len(rows)):
                    d_cells = [c.get_text(separator=' ', strip=True) for c in rows[data_row_idx].find_all(['th', 'td'])]
                    if not d_cells: continue
                    
                    current_row = {}
                    row_text_joined = " ".join(d_cells).upper()
                    for h, v in zip(headers, d_cells + ['']*(len(headers)-len(d_cells))):
                        if h and v: current_row[h] = v
                    
                    # If we don't have an anchor yet, default to the first row seen
                    if not best_row_data:
                        best_row_data = current_row
                    
                    # BUT if this row contains our specific Anchor ID, this is the absolute winner!
                    if anchor_clean and anchor_clean in row_text_joined:
                        best_row_data = current_row
                        found_target_row = True
                        break # Found exact match, stop looking in this table
                
                # Merge the best found row into main data dict
                if best_row_data:
                    # Only merge if we haven't stored this data OR if we explicitly matched the target row
                    if not data.get('mã mb') or found_target_row:
                        for k, v in best_row_data.items():
                            data[k] = v
                
                if found_target_row: break # We found the exact row needed!
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
        
        # 1. Extract Anchor Mã MB from subject FIRST to guide parsing
        subject_ma_mb = ""
        m_sub = re.search(r'(?:[^a-zA-Z0-9]|^)(MB[\s_]*\d+|MN[\s_]*\d+)', subject, re.IGNORECASE)
        if m_sub:
            subject_ma_mb = re.sub(r'[\s_]+', '', m_sub.group(1)).upper()
        
        # 2. HTML Parsing (using anchor to specifically target row)
        table_data = extract_table_from_html(html_body, anchor_ma_mb=subject_ma_mb)
        
        # Map fields from Table
        ma_mb = table_data.get('mã mb', '') or table_data.get('mã trạm', '') or table_data.get('mã site', '')
        if not ma_mb:
            # Try pattern match keys for 'mã site' or 'mã mb'
            ma_mb = next((v for k,v in table_data.items() if 'mã site' in k or 'mã mb' in k), '')
        if not ma_mb: ma_mb = subject_ma_mb # Fallback immediately to anchor
        
        ten_mb = table_data.get('tên mb', '') or table_data.get('tên mặt bằng', '') or table_data.get('tên ch', '')
        tinh = table_data.get('tỉnh', '') or table_data.get('tỉnh/thành phố', '')
        dtt = table_data.get('dtt (m2)', '') or table_data.get('dtt', '') or table_data.get('diện tích', '') or table_data.get('diện tích (m2)', '')
        
        # Scan for any value that looks like 'giá thuê gh' or 'giá thuê'
        gia_thue = table_data.get('giá thuê', '') or table_data.get('giá thuê có vat', '') or table_data.get('giá thuê có thuế', '')
        if not gia_thue:
            # Prioritize GH (Gia hạn) if present, otherwise general gia thue
            cand_gh = [v for k,v in table_data.items() if 'giá thuê' in k and 'gh' in k]
            if cand_gh: gia_thue = cand_gh[0]
            else:
                cand_gen = [v for k,v in table_data.items() if 'giá thuê' in k and 'cũ' not in k]
                if cand_gen: gia_thue = cand_gen[0]
        bct = table_data.get('thông tin bct', '') or table_data.get('bct', '')
        
        # 3. Regex Fallbacks (từ Subject và Body text)
        if not ma_mb:
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
            # Fix: Tránh bắt nhầm số 2 từ chữ '(m2)'. Kiểm tra DTT phải có số thực sự theo sau.
            m = re.search(r'(?:diện tích\s*(?:là\s*|:\s*)?|DTT\s*\([^)]*\)\s*[:\-]?\s*|DTT[^\d\n:]*[:\-]?\s*)(\d+(?:[.,]\d+)?)|(\d+(?:[.,]\d+)?)\s*m2', body, re.IGNORECASE)
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

        if not tinh:
            # Cứu cánh: Bóc tách Tỉnh nằm sát dấu ngoặc chứa mã MB ở tiêu đề
            m_tinh = re.search(r'(?:,\s*|_\s*|[:\-]\s*|^)([^,_\-:]+?)\s*\((?:MB|MN)\d+', subject, re.IGNORECASE)
            if m_tinh:
                tinh = m_tinh.group(1).strip()

        # 3. NẾU VẪN THIẾU THÔNG TIN -> XỬ LÝ ẢNH BẰNG EASYOCR
        missing = not ma_mb or not dtt or not gia_thue or not bct or not tinh
        ocr_text = ""
        if missing and msg.attachments:
            if log_callback: log_callback("📷 Dữ liệu thiếu, đang kích hoạt EasyOCR đọc ảnh...", "warn")
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
                if not tinh:
                    m_tinh = re.search(r'(?:tỉnh|t\.)\s+([A-ZÀ-Ỹ][a-zà-ỹA-ZÀ-Ỹ\s]+)', ocr_text, re.IGNORECASE)
                    if m_tinh: tinh = m_tinh.group(1).strip()
                    elif 'hải phòng' in ocr_text.lower() or 'hài phòng' in ocr_text.lower(): tinh = 'Hải Phòng'
                if not ten_mb:
                    m_ten = re.search(r'(WM\+[\sA-Z]+[A-Za-zà-ỹA-ZÀ-Ỹ\s]+)', ocr_text, re.IGNORECASE)
                    if m_ten: ten_mb = m_ten.group(1).strip()

        # Cleanups
        if ma_mb and any(kw in ma_mb.lower() for kw in ['thông tin', 'giá thuê', 'diện tích', 'dtt']): ma_mb = ''
        if dtt and re.search(r'[()]|^0\d{8,}', str(dtt)): dtt = ''
        if bct and re.match(r'^[\d.,\s]+$', bct.strip()): bct = ''
        if bct: bct = ' '.join(bct.split())
        if tinh:
            tinh = re.sub(r'^(?:T\.|Tỉnh|TP\.|Thành phố)\s+', '', tinh, flags=re.IGNORECASE).strip()

        # 4. LỚP 3: GEMINI AI RESCUE DỮ LIỆU THIẾU
        missing_fields = []
        if not ma_mb: missing_fields.append("ma_mb")
        if not ten_mb: missing_fields.append("thong_tin_mb")
        if not tinh: missing_fields.append("tinh")
        if not dtt: missing_fields.append("dtt")
        if not gia_thue: missing_fields.append("gia_thue_vat")
        if not bct: missing_fields.append("bct")
        if not cv_sender: missing_fields.append("cv_tkmb")
        
        if missing_fields and GEMINI_AVAILABLE and _gemini_client:
            if log_callback: log_callback(f"🤖 Kích hoạt Gemini Rescue để điền: {', '.join(missing_fields)}", "info")
            try:
                import json
                prompt = f"Bạn là AI phân tích email thẩm định mặt bằng. Email gửi cho To: {msg.to} / Cc: {msg.cc}\n"
                prompt += f"Nội dung: {body}\n"
                if ocr_text: prompt += f"Dữ liệu OCR từ ảnh đính kèm: {ocr_text}\n"
                prompt += f"Hãy TÌM và ĐIỀN các trường còn thiếu sau dựa vào logic (TN TKMB thường là trưởng nhóm có trong Cc. Tỉnh hoặc Tên MB có thể nằm trong thư hoặc OCR). Trả về JSON chứa đúng các key sau:\n"
                for f in missing_fields: prompt += f'- "{f}": ""\n'
                
                response = _gemini_client.models.generate_content(
                    model='gemini-3.1-flash-lite',
                    contents=prompt,
                    config={"response_mime_type": "application/json"}
                )
                ai_data = json.loads(response.text)
                
                if not ma_mb and ai_data.get('ma_mb'): ma_mb = ai_data['ma_mb']
                if not ten_mb and ai_data.get('thong_tin_mb'): ten_mb = ai_data['thong_tin_mb']
                if not tinh and ai_data.get('tinh'): tinh = ai_data['tinh']
                if not dtt and ai_data.get('dtt'): dtt = _clean_dtt(ai_data['dtt'])
                if not gia_thue and ai_data.get('gia_thue_vat'): gia_thue = _validate_gia_thue(ai_data['gia_thue_vat'])
                if not bct and ai_data.get('bct'): bct = ai_data['bct']
                
            except Exception as e:
                if log_callback: log_callback(f"Lỗi AI Rescue: {e}", "err")

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
            "ma_mb": ma_mb, "tinh_trang": detect_tinh_trang(subject, table_data),
            "thong_tin_mb": ten_mb, "tinh": tinh, "dtt": dtt,
            "gia_thue_vat": gia_thue, "bct": bct,
            "cv_tkmb": extract_cv_tkmb(cv_sender),
            "chi_tiet_thamdinh": kstt_text,
            "gia_thue_sum": summarize_gia_thue(kstt_text),
            "hspl": summarize_hspl(kstt_text),
            "ghi_chu": "",
        }
        
        for k, v in data.items():
            if isinstance(v, str):
                # 1. Chữa lỗi font hệ thống trước
                v = safe_fix_font(v)
                # 2. Xóa ký tự rác điều khiển
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
