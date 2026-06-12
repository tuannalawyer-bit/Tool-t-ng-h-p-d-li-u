import urllib.request
import urllib.parse
import json
import sys
import re
import http.cookiejar

# Thiết lập utf-8 cho stdout trên Windows
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def fetch_parcel_with_csrf(lat, lng):
    """
    Kịch bản đầy đủ để vượt qua lỗi HTTP 419 (CSRF Token Missing):
    1. Tạo CookieJar để lưu Cookie phiên làm việc.
    2. Tải trang chủ để lấy Cookie và thẻ meta csrf-token.
    3. Thực hiện POST gửi yêu cầu kèm CSRF Token.
    """
    # 1. Tạo bộ lưu Cookie và Trình xử lý yêu cầu (Opener)
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "vi,en-US;q=0.7,en;q=0.3"
    }

    print("[*] Buoc 1: Dang ket noi den Guland.vn de khoi tao phien (Session) va lay Token...")
    main_page_url = "https://guland.vn/soi-quy-hoach"
    
    req_get = urllib.request.Request(main_page_url, headers=headers)
    csrf_token = None
    
    try:
        with opener.open(req_get, timeout=15) as resp:
            html_src = resp.read().decode('utf-8')
            
            # Dung Regex tim token: <meta name="csrf-token" content="...">
            token_match = re.search(r'name=["\']csrf-token["\']\s+content=["\'](.*?)["\']', html_src)
            if token_match:
                csrf_token = token_match.group(1)
                print(f"[+] Da tim thay CSRF Token: {csrf_token[:10]}...")
            else:
                # Thu kieu viet nguoc lai: content="..." name="csrf-token"
                token_match_rev = re.search(r'content=["\'](.*?)["\']\s+name=["\']csrf-token["\']', html_src)
                if token_match_rev:
                    csrf_token = token_match_rev.group(1)
                    print(f"[+] Da tim thay CSRF Token: {csrf_token[:10]}...")
                else:
                    print("[-] Canh bao: Khong tim thay CSRF token trong HTML.")
    except Exception as e:
        print(f"[-] Loi khi tai trang chu: {str(e)}")
        return None

    # 2. Thuc hien gui yeu cau POST lay thong tin
    api_url = "https://guland.vn/get-bound-2"
    
    data_payload = {
        "lat": lat,
        "lng": lng
    }
    encoded_data = urllib.parse.urlencode(data_payload).encode('utf-8')
    
    post_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": main_page_url
    }
    
    # Neu tim thay csrf-token thi gan vao header
    if csrf_token:
        post_headers["X-CSRF-TOKEN"] = csrf_token

    req_post = urllib.request.Request(api_url, data=encoded_data, headers=post_headers, method='POST')
    
    print(f"[*] Buoc 2: Dang gui POST request den {api_url}...")
    try:
        with opener.open(req_post, timeout=15) as response:
            if response.status == 200:
                response_text = response.read().decode("utf-8")
                try:
                    return json.loads(response_text)
                except ValueError:
                    print("[-] Loi: Khong phai dinh dang JSON.")
                    return None
            else:
                print(f"[-] HTTP Status Loi: {response.status}")
                return None
    except urllib.error.HTTPError as e:
        print(f"[-] Loi HTTP {e.code}: Cần kiểm tra xem trang có chặn Cloudflare hay không.")
        return None
    except Exception as e:
        print(f"[-] Loi khi goi API: {str(e)}")
        return None

def parse_plot_html(html_content):
    """
    Regex parsing de lay du lieu tho tu html tra ve
    """
    if not html_content:
        return {}
    clean_html = html_content.replace('\n', ' ').replace('\r', '')
    results = {}
    
    match_to = re.search(r'Tờ\s*<b>(.*?)</b>', clean_html)
    match_thua = re.search(r'Thửa\s*<b>(.*?)</b>', clean_html)
    match_dt = re.search(r'Diện tích\s*<b>(.*?)</b>', clean_html)
    
    if match_to: results['to_ban_do'] = match_to.group(1).strip()
    if match_thua: results['so_thua'] = match_thua.group(1).strip()
    if match_dt: results['dien_tich'] = match_dt.group(1).strip()
    
    address_matches = re.findall(r'<a[^>]*>(.*?)</a>', clean_html)
    if address_matches:
        cleaned_addr = [a.strip() for a in address_matches if 'độ' not in a and 'vẽ' not in a and 'đường' not in a and 'hiệu' not in a]
        results['administrative_address'] = " - ".join(cleaned_addr)
        
    land_types = []
    type_pattern = re.findall(r'<button[^>]*class="[^"]*btn-land[^"]*"[^>]*>\s*([A-Z0-9]+)\s*</button>\s*([\d\.]+m²)\s*(.*?)(?=<br|</div>|&nbsp;|<button)', clean_html)
    if type_pattern:
        for code, area, desc in type_pattern:
            desc_clean = re.sub(r'<[^>]+>', '', desc).strip()
            land_types.append({"code": code, "area": area, "description": desc_clean})
    results['land_types'] = land_types
    return results

if __name__ == "__main__":
    # Toa do mau building tai trung tam TP.HCM (Quan 1) de dam bao tra ve du lieu
    target_lat = 10.77685
    target_lng = 106.70085
    
    result = fetch_parcel_with_csrf(target_lat, target_lng)
    
    if result:
        print("\n" + "="*60)
        print("🎉 THANH CONG! KET QUA TRUY XUAT THONG TIN")
        print("="*60)
        
        points = result.get('points', [])
        if points is None: points = []
        print(f"[+] Ranh gioi polygon: Co {len(points)} diem toa do.")
        
        html_data = result.get('html', '')
        if html_data:
            parsed = parse_plot_html(html_data)
            print("\n📊 CHI TIET THUA DAT:")
            print(f"  📍 Dia chi: {parsed.get('administrative_address', 'N/A')}")
            print(f"  📄 So To: {parsed.get('to_ban_do', 'N/A')}  |  🔖 So Thua: {parsed.get('so_thua', 'N/A')}")
            print(f"  📏 Dien tich: {parsed.get('dien_tich', 'N/A')}")
            
            print("\n📑 QUY HOACH SU DUNG DAT:")
            for l in parsed.get('land_types', []):
                print(f"  • [{l['code']}] Dien tich {l['area']} -> {l['description']}")
        
        with open("plot_bound_response.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=4)
        print("\n[+] Da luu file JSON.")
        print("="*60 + "\n")
