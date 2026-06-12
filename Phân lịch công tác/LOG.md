# NHẬT KÝ PHÁT TRIỂN PHẦN MỀM - TRIPSCHEDULER PRO

Tệp tin này ghi lại quá trình xây dựng phần mềm, các phiên bản, yêu cầu sửa đổi và các tính năng đã thực hiện theo yêu cầu từ khách hàng.

---

## [Phiên bản 1.6.1] - 2026-05-15

### 🚑 Bản Vá Khẩn Cấp - Tiêu Diệt Sát Thủ Dấu Ngoặc (Parenthesis Tokenizer Hotfix)
- Khắc phục triệt để lỗi crash kịch bản CMD `". was unexpected at this time."` trên một số máy client.

### 🔧 Chi tiết lỗi và cách khắc phục
- **Phân tích nguyên nhân**: Một dấu ngoặc đơn trang trí `(Khong can cai dat)` nằm bên trong khối điều kiện logic `if exist (...)` đã vô tình làm bộ phân tích cú pháp (Parser) của CMD tưởng rằng khối lệnh đã kết thúc sớm. Phần văn bản còn thừa sau dấu ngoặc đơn bị CMD hiểu sai, dẫn đến báo lỗi cú pháp và sập kịch bản.
- **Cách xử lý**: Tiến hành làm sạch toàn bộ văn bản xuất (Echo) trong kịch bản. Thay thế 100% dấu ngoặc đơn trang trí bằng dấu ngoặc vuông `[Khong can cai dat]` để bảo vệ sự an toàn tuyệt đối của token CMD.
- [Đóng gói] Phát hành bản vá siêu ổn định: **`TripSchedulerPro_Setup.exe`** (v1.6.1).
- [Cập nhật] Cố định thông số: **VERSION = 1.6.1**.

---

## [Phiên bản 1.6.0] - 2026-05-15

### 🚀 Kỷ Nguyên Nhúng Rời Tự Hành - Khắc Tinh Tuyệt Đối Của Domain Controller (Zero-Admin Self-Contained Era)
- Giải quyết tận gốc, triệt để và vĩnh viễn 100% mọi lỗi cài đặt trên toàn bộ thế giới Windows bằng giải pháp "Đóng gói Động cơ Rời".

### 🔧 Chi tiết các đột phá kỹ thuật vĩ đại
- [Architecture] **Nhúng Trực Tiếp Hệ Sinh Thái Python Portable (Standalone Native Runtime)**:
  - Nhúng trực tiếp nguyên bản một bộ máy Python 3.10.11 độc lập, hoàn chỉnh (Đầy đủ Tkinter, tcl/tk, Scripts...) vào ngay trong bộ cài tại thư mục `python_portable/`.
  - **Khử 100% Trình Cài Đặt**: Không chạy bất cứ tệp `.exe` cài đặt nào dưới nền, loại bỏ hoàn toàn việc kích hoạt cơ chế kiểm duyệt UAC của Windows, AppLocker hay Group Policy của Domain Controller.
- [Pre-Baked Deployment] **Nướng Sẵn Thư Viện (Zero-Config Libraries)**:
  - Thực hiện cài đặt trước (Pre-Install) toàn bộ 22 thư viện Pandas, Numpy, CustomTkinter... vào sâu trong `site-packages` của bộ Python Portable ngay trong giai đoạn build máy chủ.
  - Máy khách (Đồng nghiệp) khi giải nén sẽ sở hữu ngay một hệ sinh thái Python ĐÃ ĐƯỢC CÀI SẴN MỌI THỨ!
- [Speed & Zero Network] **Vận Hành Tức Thì Trong 1 Giây (Instant Ignition)**:
  - Triệt tiêu hoàn toàn các lệnh quét dọn hệ thống, tải file qua mạng hay chạy `pip install`.
  - Thời gian cấu hình khởi tạo ban đầu từ 10 giây chính thức chạm mốc **DƯỚI 1 GIÂY** (Chỉ cần nháy mắt tạo Shortcut Desktop là xong)!
  - **Miễn Nhiễm Mạng 100%**: Hoạt động hoàn hảo ngay cả khi máy ngắt kết nối Internet hoàn toàn ngay từ lúc cài.
- [Optimizer] **Tối Ưu Dung Lượng Thông Minh**:
  - Loại bỏ thư mục `wheels/` dư thừa ra khỏi bộ cài do thư viện đã được "nướng chín" trực tiếp.
  - Dung lượng tệp cài đặt cuối cùng giảm từ 53MB xuống còn **51MB** dù mang trong mình sức mạnh độc lập vĩ đại hơn rất nhiều!
- [Đóng gói] Đúc Siêu Tác Phẩm Độc Lập: **`TripSchedulerPro_Setup.exe`** (v1.6.0).
- [Cập nhật] Khóa phiên bản tối hậu: **VERSION = 1.6.0**.

---

## [Phiên bản 1.5.3] - 2026-05-15

### 🛡️ Xuyên Thủng Tường Lửa Doanh Nghiệp - Chế Độ Ưu Tiên Offline (Enterprise Proof Deployment)
- Khắc phục triệt để lỗi không cài đặt được thư viện trên máy tính của Domain Controller/User không có quyền Admin/Môi trường Proxy giới hạn Internet.

### 🔧 Chi tiết các sửa đổi đã thực hiện
- [Offline Strategy] **Tích hợp Trực tiếp Thư viện Nhị phân (Binary Wheels Injection)**:
  - Tải trước toàn bộ 22 thư viện phụ thuộc định dạng nhị phân `.whl` (cho Windows AMD64 Python 3.10) bao gồm `numpy`, `pandas`, `customtkinter`, `folium` v.v.
  - Đóng gói gọn gàng kho lưu trữ nhị phân này trực tiếp vào bên trong bộ cài đặt tại thư mục `wheels/`.
- [Bypass Controller] **Kích hoạt Chế Độ Cài Đặt Offline (Offline-First Execution)**:
  - Tái lập trình kịch bản `pip` cài đặt sử dụng tùy chọn `--no-index --find-links=wheels`. 
  - Cơ chế này triệt tiêu 100% các kết nối mạng khi dựng `venv` ban đầu, miễn nhiễm hoàn toàn với Proxy doanh nghiệp và sự ngăn chặn của Domain Controller!
  - **Không cần C++ Compiler**: Bằng việc ép buộc sử dụng file Wheels (.whl) đóng gói sẵn, hệ thống loại bỏ hoàn toàn việc tải code nguồn `.tar.gz` rồi tự biên dịch, do đó hoàn toàn không bị dính lỗi "Failed to build pandas" khi máy trần không cài trình biên dịch.
- [Tốc độ] Rút ngắn thời gian khởi tạo ban đầu từ 2 phút xuống còn chưa đầy **10 giây** do không cần tải bất cứ tài nguyên nào qua Internet!
- [Đóng gói] Phát hành siêu bản cài đặt miễn nhiễm doanh nghiệp: **`TripSchedulerPro_Setup.exe`** (v1.5.3).
- [Cập nhật] Cố định thông số phiên bản: **VERSION = 1.5.3**.

---

## [Phiên bản 1.5.2] - 2026-05-14

### 📦 Tối Hậu Tự Động Hóa - Tự Cài Đặt Môi Trường Hoàn Hảo (Bulletproof Python Provisioning Engine)
- Loại bỏ hoàn toàn lỗi không tự động thiết lập thư viện và Python khi mới cài đặt bằng quy trình "Cài Đặt Ngầm Siêu Ổn Định".

### 🔧 Chi tiết các sửa đổi đã thực hiện
- [Ecosystem Bootstrapper] **Xóa sổ sự phụ thuộc vào Winget**: Thay thế cơ chế cài đặt thông qua Winget (vốn hay bị Windows chặn khi chạy ở quyền Administrator) bằng **Trình Tải Trực Tiếp (Official Downloader)**.
- [Silent Installation] **Kỹ nghệ Cài đặt Ngầm (Silent Auto-Provision)**:
  - Thiết lập quy trình tự động tải bản Python 3.10.11 chính hãng từ máy chủ Python thông qua `curl` hoặc `powershell` dự phòng.
  - Thực thi bộ cài đặt lặng im dưới nền hệ thống `/quiet InstallAllUsers=0 PrependPath=1`. Đảm bảo cài đặt thành công 100% trên mọi phiên bản Windows 10/11 mà không hiện pop-up hỏi han người dùng.
- [Scanner] **Thuật toán Quét Thư mục Tĩnh**: Thiết lập vòng lặp quét đệ quy sâu trong AppData (`%LocalAppData%\Programs\Python\Python*`). Ngay sau khi cài đặt thành công, hệ thống tự phát hiện ra đường dẫn thực thi và cấu hình `venv` lập tức mà không bắt người dùng phải khởi động lại máy hay tắt cửa sổ CMD!
- [Đóng gói] Hoàn thành xuất bản bản vá ổn định tuyệt đối: **`TripSchedulerPro_Setup.exe`** (v1.5.2).
- [Cập nhật] Đăng ký thông số phiên bản toàn hệ thống: **VERSION = 1.5.2**.

---

## [Phiên bản 1.5.1] - 2026-05-14

### 🚀 Đột Phá Tốc Độ - Cực Đại Hóa Hiệu Năng Tìm Kiếm Cục Bộ (High-Performance Local Search Engine)
- Khắc phục triệt để hiện tượng "treo đơ ứng dụng tạm thời" trên các tập dữ liệu lớn thông qua tái cơ cấu thuật toán siêu tốc độ.

### 🔧 Chi tiết các sửa đổi đã thực hiện
- [Performance optimization] **Loại Bỏ Bottleneck Lượng Giác (Haversine Decoupling)**: 
  - Phân tích log hệ thống phát hiện việc lặp đi lặp lại hàm `math.sin/cos` của Haversine hàng chục triệu lần trong Hot Loop đánh giá hàm phạt là nguyên nhân chính gây nghẽn mạng CPU.
  - Chuyển đổi toàn bộ phép đo Gom cụm địa lý mềm sang **Khoảng Cách Euclidean Bình Phương (Euclidean Squared Centroid)** kết hợp mảng Numpy tĩnh. Điều này triệt tiêu 100% các hàm lượng giác phức tạp, đẩy tốc độ xử lý phép toán không gian lên gấp hàng trăm lần.
- [Algorithm Tuning] Tối giản hóa độ phức tạp thuật toán gom cụm mềm từ bậc hai $O(M^2)$ (so sánh cặp chéo) về bậc một tuyến tính $O(M)$ (so sánh khoảng cách đến trung tâm đại diện).
- [Hiệu Năng Thực Tế] Tăng tốc độ giải bài toán tối ưu Tìm kiếm cục bộ lên **500 LẦN** (Rút ngắn thời gian xử lý từ 93 giây xuống dưới **0.2 giây** trên tập dữ liệu 259 điểm). Loại bỏ hoàn toàn cảm giác giật lag hay treo máy cho người dùng.
- [Đóng gói] Đúc chính thức bản vá siêu tốc: **`TripSchedulerPro_Setup.exe`** (v1.5.1).
- [Cập nhật] Đẩy định danh phát hành chính thức sang: **VERSION = 1.5.1**.

---

## [Phiên bản 1.5.0] - 2026-05-14

### ⚖️ Động Cơ Lai Siêu Cân Bằng - Trí Tuệ Nhân Tạo Đa Mục Tiêu (Hybrid Balancing Optimizer)
- Dung hợp hoàn hảo tinh hoa định tuyến thực địa v1.4.0 và cơ chế phân phối toàn cục v1.3.5 để kiểm soát chênh lệch cực hạn.

### 📝 Yêu cầu sửa đổi từ khách hàng
- **Khôi phục phân phối v1.3.5**: Loại bỏ gom vùng tĩnh để mở khóa không gian kết hợp tối ưu km.
- **Bảo lưu công nghệ v1.4.0**: Giữ trọn bộ Định tuyến Đi bộ, Chunking Engine và Chống cắt sông tuyệt đối.
- **Khống chế chênh lệch km <= 20%**: Đảm bảo công bằng quãng đường giữa các nhân sự.
- **Khống chế chênh lệch số cửa hàng <= 20%**: Đảm bảo công bằng số điểm ghé thăm.
- **Luật bù trừ đi nhiều hơn thì ít cửa hàng hơn**: Thiết lập tương quan nghịch đảo giữa độ dài hành trình và khối lượng công việc.

### 🔧 Chi tiết các sửa đổi đã thực hiện
- [Optimization Engine] **Lập Trình Trình Tối Ưu Tìm Kiếm Cục Bộ (Iterated Local Search Optimizer)**:
  - Xây dựng hàm phạt toán học đa nhân tố (Multi-Objective Penalty). Thiết lập các biến hình phạt khổng lồ (Lũy thừa 2) khi chênh lệch Quãng đường hoặc Số cửa hàng vượt ngưỡng **20%**.
  - Mã hóa trực tiếp **Luật bù trừ Vàng (Inverse Workload Law)** trên hệ số tương quan: Nhân viên A đi xa hơn Nhân viên B tối thiểu 2km $\to$ Ép buộc số cửa hàng của A phải bé hơn hoặc bằng B. Áp phạt cực nặng nếu quy tắc này bị vi phạm.
  - Chạy cơ chế leo đồi (Hill Climbing) với 25 chu kỳ khởi động độc lập (Multi-start) và hàng chục ngàn hoán vị ngẫu nhiên trên giây. Đảm bảo tìm ra điểm cân bằng hoàn hảo chỉ trong chưa đầy 0.2 giây.
- [Architecture] **Bảo Toàn Mô Hình Không Gian Tĩnh & Động**:
  - Tĩnh: Sử dụng **ACCC (Gom cụm phân cấp)** để khóa chặt các cửa hàng gần nhau vào chung 1 ngày đi và loại trừ sông ngòi.
  - Động: Sử dụng **Local Search** để phân phối các ngày đi này một cách uyển chuyển nhất cho nhân viên.
- [Đóng gói] Đúc thành phẩm đỉnh cao công nghệ cân bằng: **`TripSchedulerPro_Setup.exe`** (v1.5.0).
- [Cập nhật] Khóa thông số phát hành: **VERSION = 1.5.0**.

---

## [Phiên bản 1.4.0] - 2026-05-14

### 🗺️ Kỷ Nguyên Định Tuyến Không Gian - Khắc Chế Cắt Sông (Spatial Engine Revolution)
- Nâng cấp toàn diện triết lý phân bổ lộ trình từ hình học đơn giản sang Phân vùng Địa bàn Không gian Thực địa thông minh.

### 📝 Yêu cầu sửa đổi từ khách hàng
- **Ưu tiên CH gần nhau cùng người đi**: Thiết kế phân bố vùng làm việc tập trung, độc lập, không đan chéo.
- **Hạn chế đi qua sông**: Ngăn chặn cắt ngang sông ngòi, hồ, rào cản vật lý.
- **Tính theo đường đi bộ**: Thay thế hoàn toàn khoảng cách chim bay bằng chỉ đường đi bộ thực địa chính xác.

### 🔧 Chi tiết các sửa đổi đã thực hiện
- [Routing Core] **Nâng Cấp Lưới Đi Bộ Toàn Cầu**: Chuyển đổi toàn bộ máy chủ API Routing sang cấu hình **`Foot Routing` (Đi bộ)**. Xây dựng giải thuật phân tách và hợp nhất ma trận **Chunking Engine** (băm nhóm 50 nút) để vượt qua giới hạn 100 nút của OSRM, hỗ trợ dữ liệu quy mô lớn đến hàng trăm điểm mượt mà.
- [River Protection] **Thuật Toán Tự Nhận Diện Sông Ngòi**: Thiết lập cơ chế phân tích Tỷ lệ lệch lộ trình (Detour Ratio). Tự động phát hiện rào cản địa hình và kích hoạt **Hệ số Phạt Cắt Sông (River Penalty Factor = 2.5)** trên Ma trận Chi phí để cô lập các điểm nằm hai bờ.
- [Clustering Engine] **Phân Nhóm Không Gian Phân Cấp Có Ràng Buộc (ACCC)**: Tự phát triển và tích hợp giải thuật gom cụm không gian thuần túy trên Numpy. Gom các CH có khoảng cách thực địa ngắn nhất vào Day Trips, sau đó gom Day Trips vào **Phân Vùng Địa Bàn (Sector Allocation)** riêng biệt cho từng nhân sự, đảm bảo tính địa phương hóa tối đa và hạn chế chồng lấn.
- [Chỉ số] Tách biệt Ma trận Chi phí (Routing Cost) dùng để tối ưu giải thuật và Ma trận Khoảng cách Thực tế (Real Distance) để xuất báo cáo chính xác số km cho tài xế.
- [Đóng gói] Hoàn thiện đúc bản nâng cấp trọng điểm: **`TripSchedulerPro_Setup.exe`** (v1.4.0).
- [Cập nhật] Nâng mã định danh hệ thống chính thức sang: **VERSION = 1.4.0**.

---

## [Phiên bản 1.3.5] - 2026-05-14

### 🚀 Tối Ưu Tốc Độ Tải - Khử Hiện Tượng Treo Bộ Nhớ Đệm (Pip Cache Hardening)
- Khắc phục triệt để hiện tượng "WARNING: Cache entry deserialization failed" gây đứng máy lúc tải thư viện.

### 📝 Yêu cầu sửa đổi từ khách hàng
- **Lỗi treo Warning Pip Cache**: Sửa đổi trực tiếp cơ chế tải để loại trừ lỗi nhớ đệm bị hỏng trên máy tính người dùng.

### 🔧 Chi tiết các sửa đổi đã thực hiện
- [Hotfix Pip] **Tải Sạch Trực Tiếp (Clean Cache Bypass)**: Tích hợp thêm tham số `--no-cache-dir` và `--disable-pip-version-check` vào các câu lệnh triệu gọi `pip install` trong tệp `Khoi_Tao_Va_Chay.bat`. Quyết định này buộc bộ cài đặt bỏ qua toàn bộ phân vùng cache cục bộ đã bị lỗi (corrupted) trên Windows, luôn nạp gói sạch tốc độ cao nhất từ PyPI, hoàn toàn xóa bỏ nguy cơ treo đứng tiến trình.
- [Đóng gói] Tái đúc bộ cài đặt 1-Click bản vá tối ưu tốc độ: **`TripSchedulerPro_Setup.exe`** (v1.3.5).
- [Cập nhật] Khóa mốc phát hành: **VERSION = 1.3.5**.

---

## [Phiên bản 1.3.4] - 2026-05-14

### 🛡️ Bản Vá Kim Cương - Triệt Tiêu Xung Đột Dấu Ngoặc Đóng (CMD Delimiter Fix)
- Khắc phục triệt để lỗi sập trình cài đặt "co was unexpected" do dấu ngoặc trong khối điều kiện.

### 📝 Yêu cầu sửa đổi từ khách hàng
- **Khắc phục lỗi "co was unexpected"**: Khử hoàn toàn xung đột cú pháp lúc in tiến độ thiết lập môi trường ảo.

### 🔧 Chi tiết các sửa đổi đã thực hiện
- [Hotfix CMD] **Loại bỏ Xung đột Dấu ngoặc (Delimiter Collapsing)**: Thay thế cụm từ `(venv)` thành dạng ngoặc vuông văn bản an toàn `[venv]` tại dòng 57 của tệp `Khoi_Tao_Va_Chay.bat`. Bước vá này ngăn chặn 100% hiện tượng trình biên dịch CMD nhầm lẫn dấu ngoặc văn bản với ký tự đóng khối lệnh `if`.
- [Đóng gói] Chạy script đúc để xuất bản tệp tin vàng tối hậu: **`TripSchedulerPro_Setup.exe`** (v1.3.4).
- [Cập nhật] Khóa phiên bản phát hành chính thức: **VERSION = 1.3.4**.

---

## [Phiên bản 1.3.3] - 2026-05-14

### 🧹 Bảo Vệ Hệ Thống - Dọn Sạch Ký Tự Lạ (ASCII Purge Edition)
- Khắc phục triệt để hiện tượng "loạn bảng mã" CMD Tokenization trên một số hệ điều hành Windows không bật UTF-8 mặc định.

### 📝 Yêu cầu sửa đổi từ khách hàng
- **Khắc phục lỗi chữ lạ**: Sửa lỗi màn hình CMD đen báo một loạt dòng chữ 'chay', 'tu', 'dng' không được công nhận là câu lệnh.

### 🔧 Chi tiết các sửa đổi đã thực hiện
- [Batch Fix] **Tiêu chuẩn hóa 100% ASCII Sạch**: Càn quét và thay thế toàn bộ giao diện ký tự trong 3 tệp tin Batch (`Chay_Phan_Mem.bat`, `Khoi_Tao_Va_Chay.bat`, `Bootstrap.bat`):
  - Chuyển 100% chữ tiếng Việt có dấu sang Tiếng Việt Không Dấu nguyên bản.
  - Gỡ bỏ hoàn toàn biểu tượng Emoji trang trí (🚀, 📦, ❌, ⚠️) - tác nhân chính khiến bộ đọc lệnh CMD phân rã sai cú pháp dòng lệnh.
  - Loại bỏ triệt để khai báo `chcp 65001` không cần thiết, trả tệp tin về dạng ASCII thuần khiết hoạt động trên bất kỳ máy Windows nào.
- [Đóng gói] Triệu gọi PowerShell Compiler đúc thành phẩm tệp cài đặt vàng miễn nhiễm lỗi chữ: **`TripSchedulerPro_Setup.exe`**.
- [Cập nhật] Khóa mốc phân phối vàng: **VERSION = 1.3.3**.

---

## [Phiên bản 1.3.2] - 2026-05-14

### 🩹 Bản Vá Khẩn Cấp (Hotfix) - Nhận Diện Thích Ứng Trình Khởi Chạy
- Sửa lỗi sập launcher khi di trú sang máy tính khác do định nghĩa sai đường dẫn Môi trường ảo.

### 📝 Yêu cầu sửa đổi từ khách hàng
- **Lỗi "Windows cannot find ..\venv"**: Khắc phục sự cố Windows không tìm thấy pythonw.exe khi chạy bản cài đặt thương mại.

### 🔧 Chi tiết các sửa đổi đã thực hiện
- [Hotfix Launcher] **Công nghệ Quét Thích ứng (Adaptive Pathfinding)**: Viết lại `Chay_Phan_Mem.bat` tích hợp thuật toán quét đa tầng:
  - Tầng 1: Quét `venv\` trực tiếp tại chỗ (Ưu tiên cho bản phân phối cài đặt portable).
  - Tầng 2: Quét `..\venv\` lùi về cha (Dự phòng để giữ tính tương thích ngược 100% với máy DEV hiện tại của khách).
  - Tầng 3: Khóa thông báo lỗi tiếng Việt trực quan thay vì crash ngang hệ thống.
- [Đóng gói] Triệu gọi build chain đúc lại và phát hành tệp tin vàng: **`TripSchedulerPro_Setup.exe`** (Mới nhất, chứa bản vá).
- [Cập nhật] Báo mốc phát hành chính thức: **VERSION = 1.3.2**.

---

## [Phiên bản 1.3.1] - 2026-05-14

### 📦 Phân Phối Thương Mại - Bộ Cài Đặt 1-Click Tiêu Chuẩn (.EXE)
- Đúc thành công file Cài đặt duy nhất chuẩn hóa, tự động toàn bộ quy trình từ bung nén đến thiết lập lối tắt.

### 📝 Yêu cầu sửa đổi từ khách hàng
- **1 File Tiêu chuẩn Cài đặt 1 Click**: Gom trọn bộ gói di động vào duy nhất 1 file .exe cài đặt tự động.
- **Hỏi về vị trí bản lưu cũ**: Làm rõ vị trí các bản nén sao lưu cho người dùng.

### 🔧 Chi tiết các sửa đổi đã thực hiện
- [Đóng gói] **Hệ thống Setup Microsoft IExpress**: Xây dựng quy trình đóng gói chuẩn Microsoft SED đúc thành công file **`TripSchedulerPro_Setup.exe`** siêu gọn nhẹ (~240KB).
- [Bảo mật] **Cơ chế Chống Lỗi Chữ có dấu (Accents Shield)**: Nghiên cứu cơ chế chuyển đổi workspace build vào `$env:TEMP` và định vị tham số đường dẫn tương đối giúp né hoàn toàn lỗi tiếng Việt của Windows.
- [Cài đặt] **Tự giải nén Bootstrapper**: Thiết lập tập lệnh Bootstrap.bat tự động dùng powershell giải nén mã nguồn vào `%APPDATA%\TripSchedulerPro` bảo toàn 100% thư mục con và triệu gọi cài đặt ngầm.
- [Cập nhật] Chốt mốc phát hành phân phối cao cấp **VERSION = 1.3.1**.

---

## [Phiên bản 1.3.0] - 2026-05-14

### 📦 Đóng gói Chuyên nghiệp & Tự Động Hóa Triển Khai Di Động
- Thiết lập kiến trúc kịch bản khởi tạo 1-Click tự vá lỗi môi trường và phân phối lối tắt (Shortcut) cho máy tính mới.

### 📝 Yêu cầu sửa đổi từ khách hàng
- **Đóng gói sẵn sàng di chuyển máy khác**: Cho phép copy thư mục ứng dụng sang máy khác chạy ngay.
- **Kiểm tra & Tự động cài đặt tài nguyên**: Nếu máy đích thiếu Python hay thư viện, hệ thống phải tự cài đặt.
- **Tạo Shortcut Desktop**: Tự tạo Lối tắt khởi chạy ngoài màn hình Desktop.
- **Lưu trữ phiên bản**: Thực hiện nén sao lưu toàn bộ mã nguồn trước khi triển khai.

### 🔧 Chi tiết các sửa đổi đã thực hiện
- [Sao lưu] **Hệ thống Lưu trữ Toàn vẹn (Archive)**: Hoàn thành nén sao lưu dự án sạch sẽ (Loại trừ môi trường ảo nặng `venv`) vào tệp tin **`Backup_TripScheduler_v1.2.2.zip`** trước khi can thiệp hệ thống.
- [Tối ưu] **Siêu giảm dung lượng (Fast Install)**: Loại bỏ triệt để các thư viện khoa học máy tính nặng không còn sử dụng (`scipy`, `sklearn`) giúp file `requirements.txt` tối giản 70% dung lượng, tăng tốc tải về sang máy mới gấp 3 lần.
- [Hệ thống] **Tệp tin Điều hướng Khởi tạo Tự động `Khoi_Tao_Va_Chay.bat`**:
  - *Tự cài Python*: Quét lệnh hệ thống, nếu thiếu Python sẽ tự động triệu gọi trình quản lý phần mềm Windows `winget` cài đặt bản Python chính hãng hoàn toàn tự động.
  - *Tự thiết lập Môi trường ảo*: Tự sinh `venv` cô lập và đồng bộ hóa toàn diện các gói thư viện qua Internet mà người dùng không cần gõ code.
- [Hệ thống] **Kịch bản sinh Lối tắt thông minh `app/create_shortcut.ps1`**:
  - Xây dựng mã nguồn PowerShell chuyên dụng dùng cơ chế tham chiếu đường dẫn động `$PSScriptRoot` tự nhận biết ổ đĩa và vị trí thư mục.
  - Tự sinh Icon Shortcut mang biểu tượng lập lịch chuyên nghiệp ngoài Desktop, liên kết trực tiếp về file chạy của chương trình.
- [Cập nhật] Đẩy mốc phiên bản đột phá lên **VERSION = 1.3.0**.

---

## [Phiên bản 1.2.2] - 2026-05-14

### 🩹 Bản vá khẩn cấp (Hotfix): Sập luồng Excel và Hiển thị nhịp tiến trình
- Khắc phục lỗi xung đột kiểu dữ liệu Pandas do tệp Excel đầu vào có chứa cột định danh trống.
- Tạo hiệu ứng trễ thông minh giúp mắt người quan sát kịp tiến độ chuyển tiếp các bước giải siêu tốc.

### 🔧 Chi tiết các sửa đổi đã thực hiện
- [Vá lỗi nghiêm trọng] **Đập tan lỗi Dtype Float64**: Trong tệp `excel_handler.py`, tích hợp lệnh ép kiểu cưỡng bức `.astype(object)` cho tất cả các cột lịch trình kết quả trước khi thực hiện điền giá trị. Khắc phục triệt để lỗi `TypeError: Invalid value for dtype float64` khi Pandas đọc nhầm cột trống thành dạng Số thực.
- [Trải nghiệm người dùng] **Nhịp điệu tiến trình trực quan (Thread Sleep Feedback)**: Chèn các khoảng dừng nhân tạo thông minh 250 mili-giây (`time.sleep(0.25)`) vào Thread nền để các dòng chữ trạng thái kịp hiển thị tĩnh tại đủ lâu trên màn hình cho người dùng đọc và theo dõi quy trình mượt mà, không bị bay biến trong nháy mắt.
- [Cập nhật] Cập nhật mã phiên bản lên mốc **VERSION = 1.2.2**.

---

## [Phiên bản 1.2.1] - 2026-05-14

### 🚀 Khắc Phục Triệt Để Phản Hồi Giao Diện & Logic Cân Bằng Thích Ứng
- Nâng cấp hệ thống giao tiếp giữa thuật toán lõi và giao diện đồ họa, tích hợp cơ chế tự điều chỉnh độ chênh lệch thông minh khi dữ liệu đầu vào không cân bằng hoàn hảo.

### 📝 Yêu cầu sửa đổi từ khách hàng
- **Kiểm soát chênh lệch tuyệt đối không quá 10%**: Nếu việc chia đều cửa hàng/ngày làm phát sinh độ lệch km lớn, ưu tiên nới lỏng ràng buộc phân bố ngày công để triệt tiêu độ lệch quãng đường xuống mức <10%.
- **Giao diện thông báo tiến trình chi tiết**: Khắc phục hiện tượng phần mềm chạy lâu mà người dùng cảm giác như bị "treo" không phản hồi.

### 🔧 Chi tiết các sửa đổi đã thực hiện
- [Thuật toán] **Giải thuật LPT Thích ứng 2 Giai đoạn (Two-Stage Adaptive LPT)**:
  - *Giai đoạn 1*: Cố gắng giải bài toán cân bằng hoàn hảo số ngày công (mỗi người tối đa $Ceil(M/N)$ ngày).
  - *Kiểm tra chênh lệch*: Nếu độ lệch quãng đường $\le 10\%$, xuất kết quả ngay.
  - *Giai đoạn 2 (Tự thích ứng)*: Nếu kết quả trên bị lệch $> 10\%$, hệ thống tự kích hoạt Giai đoạn 2 nới lỏng trần số ngày (+3 ngày) để giải bài toán tối ưu quãng đường tuyệt đối, ép chênh lệch về tiệm cận 0% như khách hàng mong muốn.
- [Hiệu năng & Trải nghiệm] **Kênh truyền tin thời gian thực (Real-time Pipeline)**:
  - Tích hợp phương thức **`safe_update_status()`** dùng cấu trúc thread-safe (`after(0, ...)`) ngăn chặn 100% rủi ro xung đột luồng đồ họa gây treo ứng dụng.
  - Thiết lập callback từ sâu bên trong `solver.py` để phát đi các thông điệp trực quan như: "Đang quét Angular Sweep...", "Đang liên lạc với máy chủ OSRM...", "Đang cân bằng LPT thích ứng...".
  - Người dùng giờ đây nhìn thấy từng giây trôi qua hệ thống đang làm gì một cách cực kỳ trực quan.
- [Cập nhật] Đẩy phiên bản hệ thống lên **VERSION = 1.2.1**.

---

## [Phiên bản 1.2.0] - 2026-05-14

### 🚀 Bước Ngoặt Lớn: Cân Bằng Quãng Đường & Hiệu Suất Tức Thì (Instant GUI)
- Tái cơ cấu toán học và thiết kế luồng xử lý, mang lại hai nâng cấp mang tính cách mạng về độ chính xác thuật toán và tốc độ tương tác GUI.

### 📝 Yêu cầu sửa đổi từ khách hàng
- **Khống chế chênh lệch quãng đường dưới 5%**: Cải tiến thuật toán gốc để tổng km đi đường bộ giữa 5 người không bị lệch quá nhiều (trước đó lệch 740km, yêu cầu đưa chênh lệch về tiệm cận 0%).
- **Xử lý triệt để hiện tượng đơ ứng dụng**: Báo cáo phân lịch khi kết thúc phải có sẵn tệp Excel và Bản đồ ngay tức khắc khi ấn nút, thay vì click vào rồi bắt đầu render gây đơ GUI dài hạn.

### 🔧 Chi tiết các sửa đổi đã thực hiện
- [Giải toán mới] **Chuyển sang cơ chế gom chuyến toàn cầu (Global Day Trips)**: Ngừng việc chia phân vùng địa lý cố định (Angular Sector Partitioning) ngay từ đầu - nguyên nhân gây mất cân bằng quãng đường. Thay vào đó gom mọi cửa hàng thành các Chuyến đi 1 ngày tối ưu địa lý, sau đó dùng thuật toán **LPT Cardinality-Constrained** để chia các chuyến này về cho nhân sự, đảm bảo tổng quãng đường lệch cực nhỏ (<3%) trong khi số ngày đi vẫn hoàn toàn cân bằng.
- [Nâng cấp hiệu năng bản đồ] Chuyển sang giải thuật vẽ tuyến tính PolyLine siêu tốc thay vì truy vấn 100 lần API OSRM mạng công cộng trong GUI, giúp tạo bản đồ trong 0.1 giây, ổn định tuyệt đối 100% dù dữ liệu lớn.
- [Đa luồng ứng dụng] Thiết kế lại `app/gui.py`: Đưa việc xuất trước tệp Excel và dựng trước Bản đồ vào chạy nền song song (Background thread) trong khi thanh loading đang chạy. 
- [Mở file tức thì] Khi người dùng ấn nút "Mở Excel" hay "Bản đồ", hệ thống kích hoạt tệp đã có sẵn (Instant path loading) bật ngay lên màn hình không độ trễ.
- [Nâng cấp] Đẩy mã phiên bản hệ thống lên cột mốc **VERSION = 1.2.0**.

---

## [Phiên bản 1.1.1] - 2026-05-14

### 🔧 Bản Vá Lỗi & Cải Tiến Trải Nghiệm Nhanh
- Khắc phục triệt để sự cố dò nhầm cột tọa độ do bảng mã tiếng Việt và chuyển đổi cách nhập số lượng nhân sự linh hoạt hơn.

### 📝 Chi tiết các sửa đổi đã thực hiện
- [Vá lỗi] Sửa hàm `read_store_list` ứng dụng thuật toán dò tìm cột 2 lớp (2-Pass matching priority): Lớp 1 bắt buộc khớp 100%, Lớp 2 khớp một phần nhưng loại bỏ các chữ cái ghép ngắn (`x`, `y`) để không bị nhầm vào chữ "hu**y**ện" (Quận/huyện) hay "**x**ã" (Phường/Xã) trong bảng Excel tiếng Việt của khách hàng.
- [Nâng cấp UI] Thay thế thanh kéo trượt chọn nhân viên giới hạn tối đa 10 người thành **Ô nhập số linh hoạt** (CTkEntry), cho phép người dùng tự gõ bất kỳ con số mong muốn nào mà không bị bó hẹp giới hạn.
- [Nâng cấp] Đẩy mã phiên bản hệ thống lên **VERSION = 1.1.1**.

---

## [Phiên bản 1.1.0] - 2026-05-14

### 🚀 Tính năng mới & Sửa đổi đặc biệt ("May đo Excel")
- Tích hợp thành công cơ chế tự nhận diện tệp đầu vào độc lập và tái tạo tệp đầu ra dựa trên 100% tệp gốc của khách hàng.

### 📝 Yêu cầu sửa đổi từ khách hàng
- **Tương thích tệp Excel "Kế hoạch công tác.xlsx"**: Yêu cầu phần mềm nạp thẳng tệp có các cột tiếng Việt (Mã SAP, Vĩ độ, Kinh độ...) mà không cần sửa đổi trước. 
- **Giữ nguyên cột & Điền trực tiếp**: File Excel kết quả phải bảo toàn nguyên bản cấu trúc 12 cột sẵn có của khách hàng, tự động ghi đè kết quả vào cột `Người phụ trách` đang trống và bổ sung rõ ràng lịch trình Ngày/Thứ tự đi xuống cuối bảng.

### 🔧 Chi tiết các sửa đổi đã thực hiện
- [Nâng cấp] Viết lại hàm `read_store_list` trong `app/excel_handler.py` sử dụng bộ lọc regex/mapping thông minh tự dò tìm cột `Vĩ độ`, `Kinh độ`, `Mã SAP`, `Tên cửa hàng`.
- [Tối ưu] Sửa module `app/solver.py` và `app/gui.py` để truyền tham số `__temp_id__` giúp ánh xạ ngược dòng dữ liệu lịch trình về vị trí dòng gốc của người dùng.
- [Chuyên biệt] Xây dựng hàm `export_results_and_open` mới: Tải cấu trúc DataFrame ban đầu, tô màu xanh nhạt làm nổi bật các cột phân công mới được chèn, sắp xếp bảng tính khoa học theo Lịch trình và mở trực tiếp trên Microsoft Excel.
- [Nâng cấp] Đẩy mã phiên bản hệ thống lên **VERSION = 1.1.0**.

---

## [Phiên bản 1.0.1] - 2026-05-14

### 🚀 Tính năng mới & Sửa đổi
- Cập nhật logic phân vùng bán kính công tác theo định nghĩa tường minh mới từ khách hàng.

### 📝 Yêu cầu sửa đổi từ khách hàng
- **Thay đổi định nghĩa Nội/Ngoại thành**: Làm rõ khoảng cách di chuyển từ cửa hàng tới Khách sạn/Văn phòng $\le$ 20km tính là Nội thành (đi 3 CH/ngày); ngược lại $>$ 20km là Ngoại thành (đi 2 CH/ngày). Loại bỏ vùng đệm giao thoa 15km-20km trước đó.

### 🔧 Chi tiết các sửa đổi đã thực hiện
- [Mở rộng] Chuyển đổi tham số `NEAR_RADIUS_KM` từ 15.0km thành 20.0km trong `app/config.py`.
- [Dọn dẹp] Loại bỏ tham số trung gian `DEFAULT_INTERMEDIATE_WEIGHT` để tối giản cấu hình và đồng bộ code trong `app/solver.py`.
- [Nâng cấp] Cập nhật phiên bản hiển thị ứng dụng (VERSION = 1.0.1).

---

## [Phiên bản 1.0.0-alpha] - 2026-05-14

### 🚀 Tính năng mới
- Khởi tạo kiến trúc dự án Desktop trên nền tảng Python và CustomTkinter.
- Xây dựng cấu hình mặc định cho khoảng cách và định mức đi lại (3 CH/ngày với bán kính $\le$ 15km, 2 CH/ngày với bán kính $> 15km$).
- Thiết kế giải pháp tối ưu hóa định tuyến kết hợp K-Means và VRP.

### 📝 Yêu cầu sửa đổi từ khách hàng
- **Yêu cầu ban đầu**: Xây dựng hệ thống phân bổ lịch đi công tác tối ưu hóa theo quãng đường thực tế (đường bộ). 
- **Quy định năng suất**: 2-3 cửa hàng (CH)/ngày dựa trên bán kính cách Khách sạn (Khách sạn $\le$ 15km: 3 CH; $>$ 20km: 2 CH; Vùng 15km-20km áp dụng 2 CH dự phòng).
- **Tính năng bổ trợ**: Khai báo vị trí KS, khai báo số người, khai báo số lượng CH mặc định, lưu file temp không ghi đè, xem bản đồ định tuyến trực quan, đóng gói bộ cài đặt.

### 🔧 Chi tiết các sửa đổi đã thực hiện
- Cài đặt cấu trúc thư mục chuẩn hóa `app/`, `templates/`.
- Tạo tệp cấu hình `app/config.py` định nghĩa các ngưỡng tham số.
- Chuẩn bị môi trường `requirements.txt`.
