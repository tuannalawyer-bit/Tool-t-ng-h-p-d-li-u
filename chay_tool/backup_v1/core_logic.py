# -*- coding: utf-8 -*-
"""Core extraction logic for Email Data Extractor - Hybrid Architecture"""
import os, re, glob, json
from datetime import datetime

try:
    from google import genai
    import PIL.Image
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

_gemini_client = None

def init_gemini(api_key):
    """Khởi tạo Gemini client với API key."""
    global _gemini_client
    _gemini_client = genai.Client(api_key=api_key)

import extract_msg

FOLDER = r"D:\TĐMB\chạy tool"
EXCEL_NAME = "form tool.xlsx"
SHEET_NAME = "01. Thẩm định giá & HSPL"
DATA_START_ROW = 4

# Tất cả các trường quản lý bắt buộc (khớp với cột Excel)
REQUIRED_FIELDS = [
    'thang', 'ngay_nhan', 'ngay_tra', 'ma_mb', 'tinh_trang',
    'thong_tin_mb', 'tinh', 'dtt', 'gia_thue_vat', 'bct',
    'cv_tkmb', 'tn_tkmb', 'chi_tiet_thamdinh', 'gia_thue_sum', 'hspl'
]

# Ánh xạ tỉnh
PROVINCE_MAP = {
    'HNI': 'Hà Nội', 'SGN': 'TP.HCM', 'HPG': 'Hải Phòng', 'BNH': 'Bắc Ninh',
    'BGG': 'Bắc Giang', 'VPC': 'Vĩnh Phúc', 'YBI': 'Yên Bái', 'SLA': 'Sơn La',
    'TNN': 'Thái Nguyên', 'PTO': 'Phú Thọ', 'NAN': 'Nghệ An', 'THA': 'Thanh Hóa',
    'HBH': 'Hòa Bình', 'HDU': 'Hải Dương', 'HYN': 'Hưng Yên', 'HTI': 'Hà Tĩnh',
    'QNH': 'Quảng Ninh', 'DBN': 'Điện Biên', 'TQU': 'Tuyên Quang', 'NBI': 'Ninh Bình',
    'HNM': 'Hà Nam', 'NDI': 'Nam Định', 'TBI': 'Thái Bình', 'LCA': 'Lào Cai',
    'LSN': 'Lạng Sơn', 'CBA': 'Cao Bằng', 'BKA': 'Bắc Kạn', 'HGI': 'Hà Giang'
}

GEMINI_PROMPT_TEXT = """Bạn là trợ lý trích xuất dữ liệu. Hãy đọc nội dung email thẩm định mặt bằng dưới đây.
Trả về KẾT QUẢ DUY NHẤT LÀ MỘT CHUỖI JSON HỢP LỆ (không có markdown, không giải thích).
Keys cần có:
- ma_mb: Mã mặt bằng (ghi liền, VD: MB07930)
- tinh_trang: Tình trạng (Mở mới/Tái ký/Đang thuê)
- thong_tin_mb: Tên mặt bằng
- tinh: Tỉnh/Thành phố
- dtt: Diện tích thuê (chỉ lấy số)
- gia_thue: Giá thuê có VAT (định dạng X.XXX.XXX)
- bct: Thông tin BCT (Tên và SĐT)
- truong_nhom: Tên Trưởng nhóm phụ trách
- chi_tiet_thamdinh: Tóm tắt kết quả thẩm định
- danh_gia_gia_thue: Đánh giá giá thuê (Phù hợp/Bất thường/Chưa bất thường)
- hspl: Đánh giá hồ sơ pháp lý
Nếu trường nào không có thông tin, để giá trị là chuỗi rỗng "". KHÔNG tự bịa dữ liệu.

[Nội dung Email]:
"""

GEMINI_PROMPT_IMAGE = """Bạn là trợ lý trích xuất dữ liệu. Hãy đọc bảng thông tin thẩm định mặt bằng trong ảnh.
Trả về KẾT QUẢ DUY NHẤT LÀ MỘT CHUỖI JSON HỢP LỆ (không markdown, không giải thích).
Keys cần có:
- ma_mb: Mã mặt bằng (ghi liền, VD: MB07930)
- dtt: Diện tích thuê (chỉ lấy số)
- gia_thue: Giá thuê (định dạng X.XXX.XXX)
- bct: Thông tin BCT (Tên và SĐT)
- truong_nhom: Tên Trưởng nhóm phụ trách
- tinh: Tỉnh/Thành phố
- thong_tin_mb: Tên mặt bằng
Nếu không tìm thấy, để giá trị là chuỗi rỗng "". KHÔNG tự bịa dữ liệu.
"""

# ─── BƯỚC 1: REGEX PARSERS ──────────────────────────────────────────────────

def _is_skip_line(line):
    """Kiểm tra dòng cần bỏ qua khi parse bảng (Link video, URL, etc.)"""
    ll = line.strip().lower()
    if 'link video' in ll: return True
    if ll.startswith('http://') or ll.startswith('https://'): return True
    if 'youtube.com' in ll or 'youtu.be' in ll: return True
    return False


def _clean_dtt(raw_dtt):
    """Xử lý DTT nhiều tầng: 'T1: 150m2, T2: 45m2' → tính tổng hoặc lấy số đầu."""
    s = str(raw_dtt).strip()
    # Nếu có nhiều tầng (T1, T2, Trệt...)
    if re.search(r'[Tt]\d|[Tt]rệt|tầng', s, re.IGNORECASE):
        nums = re.findall(r'(\d+(?:[.,]\d+)?)', s)
        if nums:
            total = sum(float(n.replace(',', '.')) for n in nums)
            return str(total) if total != int(total) else str(int(total))
    # Xóa hậu tố m2
    s = re.sub(r'\s*m2.*$', '', s, flags=re.IGNORECASE).strip()
    return s


def _validate_gia_thue(val):
    """Guard: Kiểm tra giá trị có phải giá thuê hợp lệ không.
    Trả về giá trị sạch hoặc '' nếu không hợp lệ."""
    s = str(val).strip()
    if not s: return ''
    # Loại bỏ nếu chứa URL
    if 'http' in s.lower() or 'youtube' in s.lower(): return ''
    # Loại bỏ nếu chứa nội dung KSTT
    if any(kw in s.lower() for kw in ['thông tin quy hoạch', 'thẩm định', 'kstt', 'phản hồi']): return ''
    # Loại bỏ nếu chứa Link video
    if 'link video' in s.lower(): return ''
    # Loại bỏ nếu quá dài (> 20 ký tự) và chứa chữ cái (không phải giá)
    if len(s) > 20 and re.search(r'[a-zA-ZÀ-ỹ]', s): return ''
    # Loại bỏ nếu chứa chữ cái (trừ VND, đ, m2)
    clean = re.sub(r'(VND|vnđ|đ|\s)', '', s, flags=re.IGNORECASE)
    if re.search(r'[a-zA-ZÀ-ỹ]', clean): return ''
    return s


def parse_table_from_body(body):
    data = {}
    lines = [l.strip() for l in re.split(r'[\r\n]+', body) if l.strip()]
    POSSIBLE_HEADERS = [
        'stt', 'mã mb', 'tên mb', 'tỉnh', 'dtt (m2)', 'dtt',
        'giá thuê có thuế', 'giá thuê', 'thông tin bct',
        'trưởng nhóm phụ trách', 'trưởng nhóm', 'ngày gửi',
        'nội dung thẩm định', 'kết quả thẩm định', 'thông tin mb', 'ghi chú'
    ]
    try:
        headers, val_start = [], -1
        for i in range(len(lines)):
            if lines[i].lower() in POSSIBLE_HEADERS or 'mã mb' in lines[i].lower():
                count, temp_headers = 0, []
                for j in range(i, len(lines)):
                    ll = lines[j].lower()
                    if ll in POSSIBLE_HEADERS or ll == 'mã mb' or ll == 'stt':
                        count += 1; temp_headers.append(lines[j])
                    else: break
                if count >= 3 and any('mã mb' in h.lower() for h in temp_headers):
                    headers = temp_headers; val_start = i + count; break
        if headers and val_start != -1:
            val_idx = val_start
            for h in headers[:-1]:
                # Guard: bỏ qua dòng Link video / URL khi lấy giá trị
                while val_idx < len(lines) and _is_skip_line(lines[val_idx]):
                    val_idx += 1
                if val_idx < len(lines): data[h.lower()] = lines[val_idx]; val_idx += 1
            thong_tin = []
            while val_idx < len(lines):
                line = lines[val_idx]
                if line.strip().startswith("2.") or line.strip().startswith("2 "): break
                if any(kw in line for kw in ["Trân trọng", "CÔNG TY", "WinCommerce", "WinMart", "[T]", "[M]", "[E]", "Thanks", "________________________________"]): break
                if not _is_skip_line(line):
                    thong_tin.append(line)
                val_idx += 1
            data[headers[-1].lower()] = "\n".join(thong_tin)
            return {
                "ma_mb": data.get("mã mb", ""), "ten_mb": data.get("tên mb", ""),
                "tinh": data.get("tỉnh", ""),
                "dtt": data.get("dtt (m2)", data.get("dtt", "")),
                "gia_thue": data.get("giá thuê có thuế", data.get("giá thuê", "")),
                "bct": data.get("thông tin bct", ""),
                "truong_nhom": data.get("trưởng nhóm phụ trách", data.get("trưởng nhóm", "")),
                "noi_dung": data.get("nội dung thẩm định", data.get("kết quả thẩm định", "")),
                "thong_tin_mb": data.get("thông tin mb", data.get("ghi chú", ""))
            }
    except: pass
    return data


def parse_vertical_table(body):
    data = {}
    lines = [l.strip() for l in re.split(r'[\r\n]+', body) if l.strip()]
    LABEL_MAP = {
        'dtt (m2)': 'dtt', 'dtt': 'dtt', 'diện tích': 'dtt',
        'giá thuê có thuế': 'gia_thue', 'giá thuê': 'gia_thue',
        'thông tin bct': 'bct', 'trưởng nhóm phụ trách': 'truong_nhom',
        'trưởng nhóm': 'truong_nhom', 'tên mb': 'ten_mb',
        'tỉnh': 'tinh', 'mã mb': 'ma_mb',
    }
    label_indices = []
    for i, line in enumerate(lines):
        ll = line.lower().strip()
        if ll in LABEL_MAP or any(k in ll for k in ['dtt', 'giá thuê', 'bct', 'trưởng nhóm']):
            label_indices.append(i)
    if len(label_indices) >= 3:
        start, end = label_indices[0], label_indices[-1]
        labels_block = lines[start:end+1]
        values_block = lines[end+1:end+1+len(labels_block)]
        for j, label_line in enumerate(labels_block):
            ll = label_line.lower().strip()
            key = None
            for k, v in LABEL_MAP.items():
                if k in ll: key = v; break
            if key and j < len(values_block):
                val = values_block[j].strip()
                if val and not data.get(key): data[key] = val
    return data


def extract_kstt_result(body):
    parts = re.split(r'\nFrom:', body, maxsplit=1)
    top = parts[0] if parts else body
    lines = [l.strip() for l in re.split(r'[\r\n]+', top) if l.strip()]
    result_lines, in_content = [], False
    for line in lines:
        if any(g in line for g in ["Dear", "KSTT phản hồi"]): in_content = True
        if in_content and not any(g in line for g in ["Dear anh", "Dear các", "Trân trọng", "Contact:"]):
            result_lines.append(line)
    return "\n".join(result_lines).strip()


def extract_reply_date(msg):
    try:
        d = msg.date
        if d: return d.replace(tzinfo=None)
    except: pass
    return None


def extract_original_date(body):
    m = re.search(r'Sent:\s+\w+,\s+(\w+ \d+,\s+\d{4})', body)
    if m:
        try: return datetime.strptime(m.group(1), "%B %d, %Y")
        except: pass
    m2 = re.search(r'(\d{8})_', body)
    if m2:
        try: return datetime.strptime(m2.group(1), "%Y%m%d")
        except: pass
    return None


def extract_subject_date(subject):
    m = re.search(r'(\d{8})_', subject)
    if m:
        try: return datetime.strptime(m.group(1), "%Y%m%d")
        except: pass
    return None


def detect_tinh_trang(subject):
    s = subject.lower()
    if "mở mới" in s or "mb mới" in s: return "Mở mới"
    if "đang thuê" in s or "gia hạn" in s: return "Đang thuê"
    if "tái ký" in s: return "Tái ký"
    return "Mở mới"


def summarize_gia_thue(kstt_text):
    t = kstt_text.lower()
    if "chưa có bất thường" in t or "chưa bất thường" in t: return "Giá thuê chưa bất thường"
    if "bất thường" in t: return "Bất thường"
    if "phù hợp" in t: return "Phù hợp"
    return ""


def summarize_hspl(kstt_text):
    t = kstt_text.lower()
    if "chưa có bất thường" in t or "chưa bất thường" in t or "ổn định" in t: return "Chưa bất thường"
    if "bất thường" in t: return "Bất thường"
    return ""


def extract_cv_tkmb(sender):
    if not sender: return ""
    m = re.match(r'^([^(<]+)', sender)
    return m.group(1).strip() if m else sender.strip()


# ─── BƯỚC 2: GEMINI AI RESCUE ───────────────────────────────────────────────

def call_gemini_text(raw_text):
    """Gửi nội dung text email lên Gemini để trích xuất dữ liệu."""
    if not GEMINI_AVAILABLE or not _gemini_client: return {}
    try:
        response = _gemini_client.models.generate_content(
            model='gemini-2.0-flash',
            contents=GEMINI_PROMPT_TEXT + raw_text[:8000]
        )
        return _parse_gemini_response(response.text)
    except Exception as e:
        print(f"Gemini Text Error: {e}")
        return {}


def call_gemini_image(image_path):
    """Gửi ảnh lên Gemini Vision để trích xuất dữ liệu."""
    if not GEMINI_AVAILABLE or not _gemini_client: return {}
    try:
        img = PIL.Image.open(image_path)
        response = _gemini_client.models.generate_content(
            model='gemini-2.0-flash',
            contents=[GEMINI_PROMPT_IMAGE, img]
        )
        return _parse_gemini_response(response.text)
    except Exception as e:
        print(f"Gemini Image Error: {e}")
        return {}


def _parse_gemini_response(text):
    """Parse JSON response từ Gemini, xử lý markdown wrapper."""
    text = text.strip()
    if text.startswith('```'):
        lines = text.split('\n')
        if lines[0].startswith('```'): lines = lines[1:]
        if lines and lines[-1].startswith('```'): lines = lines[:-1]
        text = '\n'.join(lines).strip()
    try:
        return json.loads(text)
    except:
        return {}


def process_images_with_gemini(msg, msg_path):
    """Xử lý tất cả ảnh đính kèm bằng Gemini Vision."""
    combined = {}
    for a in msg.attachments:
        fname = a.longFilename or a.shortFilename or ""
        if fname.lower().endswith(('.png', '.jpg', '.jpeg')) and a.data:
            temp = os.path.join(os.path.dirname(os.path.abspath(msg_path)), "_temp_" + fname)
            try:
                with open(temp, "wb") as f: f.write(a.data)
                data = call_gemini_image(temp)
                for k, v in data.items():
                    if v and not combined.get(k): combined[k] = str(v).strip()
            except: pass
            finally:
                try: os.remove(temp)
                except: pass
    return combined


# ─── BƯỚC 1+2+3: HYBRID PIPELINE ────────────────────────────────────────────

def process_msg_file(msg_path, log_callback=None):
    """Pipeline xử lý Hybrid: Regex → Gemini AI Rescue → Validation."""
    result = {"file": os.path.basename(msg_path), "path": msg_path,
              "success": False, "error": "", "data": {}, "missing_fields": []}
    msg = None
    try:
        msg = extract_msg.Message(msg_path)
        body = msg.body or ""
        subject = msg.subject or ""
        sender = msg.sender or ""
        is_reply = subject.upper().startswith("RE:")

        # ══════ BƯỚC 1: REGEX FAST TRACK ══════
        if log_callback: log_callback("⚡ Bước 1: Trích xuất bằng Regex...", "info")

        # Parse table
        table = parse_table_from_body(body)
        if not table.get("ma_mb") and not table.get("dtt"):
            table.update({k: v for k, v in parse_vertical_table(body).items() if v and not table.get(k)})

        # Extract metadata
        reply_date = extract_reply_date(msg) if is_reply else None
        orig_date = extract_subject_date(subject) or extract_original_date(body)
        cv_sender = sender
        if is_reply:
            m = re.search(r'From:\s+([^\n<]+)', body)
            if m: cv_sender = m.group(1).strip()
        kstt_text = extract_kstt_result(body) if is_reply else ""

        # Assemble data from Regex
        ma_mb = table.get("ma_mb", "")
        ten_mb = table.get("ten_mb", "")
        tinh = table.get("tinh", "")
        dtt = table.get("dtt", "")
        gia_thue = table.get("gia_thue", "")
        bct = table.get("bct", "")
        truong_nhom = table.get("truong_nhom", "")

        # Regex fallbacks for ma_mb
        if not ma_mb:
            m = re.search(r'\b(MB[\s_]*\d+|MN[\s_]*\d+)', subject, re.IGNORECASE)
            if m: ma_mb = re.sub(r'[\s_]+', '', m.group(1)).upper()
        if not ma_mb:
            m = re.search(r'\b(MB[\s_]*\d+|MN[\s_]*\d+)', body, re.IGNORECASE)
            if m: ma_mb = re.sub(r'[\s_]+', '', m.group(1)).upper()

        # Regex fallbacks for ten_mb, tinh
        if not ten_mb or not tinh:
            m = re.search(r'WM\+\s+([A-Z]{3})\s+([^()]+)', subject, re.IGNORECASE)
            if m:
                code = m.group(1).upper()
                name_part = re.sub(r'[-,\s_]+$', '', m.group(2).strip())
                if not ten_mb: ten_mb = 'WM+ ' + code + ' ' + name_part
                if not tinh: tinh = 'T. ' + PROVINCE_MAP.get(code, code)

        # Clean DTT (xử lý nhiều tầng: T1: 150m2, T2: 45m2)
        dtt = _clean_dtt(dtt)
        if not dtt or len(str(dtt)) > 20:
            m = re.search(r'(?:diện tích\s*(?:là\s*|:\s*)?|DTT[^\d\n]*)(\d+(?:[.,]\d+)?)|(\d+(?:[.,]\d+)?)\s*m2', body, re.IGNORECASE)
            if m: dtt = (m.group(1) or m.group(2)).replace(',', '.')

        # Clean & Validate gia_thue
        gia_thue = _validate_gia_thue(gia_thue)
        if not gia_thue:
            prices = re.findall(r'(?<!\d)([1-9]\d{0,2}(?:[.,]\d{3}){2,})(?!\d)', body)
            if prices: gia_thue = _validate_gia_thue(prices[-1].replace(',', '.'))

        # Clean BCT
        if bct: bct = ' '.join(bct.split())
        if not bct:
            body_phones = re.finditer(r'(?:Cô|Chú|Bác|Anh|Chị|Ông|Bà|BCT)\s*([A-Z][a-zà-ỹA-ZÀ-Ỹ\s]{1,20})?[:\-]?\s*(0\d{9})', body, re.IGNORECASE)
            for match in body_phones:
                name = match.group(1)
                n = name.strip() if name else 'BCT'
                bct = f'{n}: {match.group(2)}'; break

        # Build data dict after Step 1
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
            "ghi_chu": table.get("thong_tin_mb", ""),
        }

        # ══════ BƯỚC 2: KIỂM TRA & GEMINI AI RESCUE ══════
        missing = [f for f in REQUIRED_FIELDS if not str(data.get(f, "")).strip()]

        if missing and GEMINI_AVAILABLE:
            if log_callback: log_callback(f"🤖 Bước 2: AI Rescue - Thiếu {len(missing)} trường: {missing}", "warn")

            # 2a: Gemini Vision cho ảnh đính kèm
            img_data = process_images_with_gemini(msg, msg_path)

            # 2b: Gemini Text cho nội dung email
            text_data = call_gemini_text(body[:8000])

            # Map Gemini keys vào data keys
            KEY_MAP = {
                'ma_mb': 'ma_mb', 'tinh_trang': 'tinh_trang',
                'thong_tin_mb': 'thong_tin_mb', 'tinh': 'tinh',
                'dtt': 'dtt', 'gia_thue': 'gia_thue_vat',
                'bct': 'bct', 'truong_nhom': 'tn_tkmb',
                'chi_tiet_thamdinh': 'chi_tiet_thamdinh',
                'danh_gia_gia_thue': 'gia_thue_sum', 'hspl': 'hspl',
            }
            # Merge: chỉ điền vào ô trống
            for gemini_data in [img_data, text_data]:
                for gk, dk in KEY_MAP.items():
                    val = gemini_data.get(gk, "")
                    if val and not str(data.get(dk, "")).strip():
                        data[dk] = str(val).strip()
        elif missing:
            if log_callback: log_callback(f"⚠️ Thiếu {len(missing)} trường nhưng Gemini chưa sẵn sàng", "warn")

        # ══════ BƯỚC 3: VALIDATION & PHÂN LOẠI ══════
        final_missing = [f for f in REQUIRED_FIELDS if not str(data.get(f, "")).strip()]

        result["data"] = data
        result["missing_fields"] = final_missing

        if not final_missing:
            result["success"] = True
            if log_callback: log_callback("✅ Thành công: Đã trích xuất đầy đủ 100% các trường quản lý.", "ok")
        else:
            # Vẫn đánh dấu success=True nếu có Mã MB (để GHI vào Excel)
            # nhưng ghi nhận missing_fields để đổi tên failed_
            if data.get("ma_mb"):
                result["success"] = True  # Vẫn ghi Excel
                result["partial"] = True  # Đánh dấu thiếu dữ liệu
                if log_callback:
                    field_names = ", ".join(final_missing)
                    log_callback(f"❌ Thất bại một phần: Khuyết [{field_names}]", "err")
            else:
                result["success"] = False
                result["error"] = "Không tìm được Mã MB"

    except Exception as e:
        result["error"] = str(e)
    finally:
        if msg:
            try: msg.close()
            except: pass
    return result
