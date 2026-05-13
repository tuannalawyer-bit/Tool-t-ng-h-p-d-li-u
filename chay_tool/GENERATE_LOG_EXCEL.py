import openpyxl
from openpyxl.styles import Font, Fill, PatternFill, Alignment, Border, Side
import os

output_path = r"D:\chạy tool\chạy tool\LICH_SU_PHAT_TRIEN_TOOL.xlsx"
target_dir = os.path.dirname(output_path)
if not os.path.exists(target_dir):
    output_path = r"d:\Dự án AI\chay_tool\LICH_SU_PHAT_TRIEN_TOOL.xlsx"

wb = openpyxl.Workbook()
ws = wb.active
ws.title = "Nhật ký Chỉnh sửa"

# Style Headers
hdr_font = Font(bold=True, color="FFFFFF", size=12)
hdr_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
center_align = Alignment(horizontal="center", vertical="center", wrap_text=True)
left_align = Alignment(horizontal="left", vertical="top", wrap_text=True)
thin_border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))

headers = ["STT", "Thời Gian", "Yêu Cầu / Tình Trạng Lỗi", "Kết Quả Phân Tích Kỹ Thuật", "Nội Dung Nâng Cấp / Khắc Phục", "Phiên Bản Áp Dụng"]
ws.append(headers)

for i in range(1, 7):
    cell = ws.cell(row=1, column=i)
    cell.font = hdr_font
    cell.fill = hdr_fill
    cell.alignment = center_align
    cell.border = thin_border

data = [
    [
        1, "Hôm qua (Đầu Kỳ)", "Yêu cầu tích hợp EasyOCR và Giao diện hiện đại",
        "Đã hoàn thiện nền tảng Hybrid (Regex + OCR) cùng với GUI v2.0 ổn định nhất.",
        "Tạo bản sao lưu Vàng 'core_logic_backup_truoc_AI.py' tại mốc này để đảm bảo an toàn.",
        "v2.0 Golden Stable"
    ],
    [
        2, "Hôm nay (08:00 AM)", "Phát sinh yêu cầu Tự động phân tích sâu rủi ro HSPL và Giá thuê vào 3 cột cuối cùng.",
        "Khi đẩy AI làm nhiệm vụ Suy luận phân tích phức tạp, số lượng yêu cầu (API calls) tăng đột biến 100% cho mỗi Email.",
        "Code cũ gọi lệnh .strip() bị lỗi Crash do AI thông minh trả về danh sách (List) thay vì văn bản.",
        "v2.5 Dev (Experimental)"
    ],
    [
        3, "Hôm nay (08:15 AM)", "Thông báo lỗi: 429 Resource Exhausted",
        "Tài khoản đã cạn kiệt hạn mức Ngày (500 calls) của model 3.1 Flash-Lite và chạm giới hạn Giây (5 calls/phút) của bản 2.5.",
        "Nâng cấp hàm _safe_str() chống Crash kiểu dữ liệu. Chuyển đổi sang Model 2.5 và cài đặt Vòng lặp tự hồi phục (Wait 15s).",
        "v2.6 Patch Alpha"
    ],
    [
        4, "Hôm nay (08:35 AM)", "Lỗi lặp lại và tốc độ giảm do dính Quota - User yêu cầu hoàn tác khẩn cấp.",
        "Hệ thống thử nghiệm phân tích sâu chưa tối ưu cho gói API miễn phí, gây phiền toái về tốc độ cho người dùng.",
        "Thực hiện Lệnh Khôi Phục Đặc Biệt (Rollback) từ File Vàng 'core_logic_backup_truoc_AI.py'.",
        "v2.0 Golden (Restored)"
    ],
    [
        5, "HIỆN TẠI", "Khôi phục hoàn chỉnh 100% hệ thống vận hành an toàn.",
        "Xác nhận Model Gemini 3.1 Flash-Lite đang chạy ổn định ở chế độ 'Giải cứu' (Rescue Mode) - Không gây tải cho API.",
        "Lưu trữ bản gốc vào Core Logic chính thức, khóa cứng hệ thống vào trạng thái ổn định tuyệt đối.",
        "PHIÊN BẢN HOÀN HẢO HIỆN HÀNH"
    ]
]

row_idx = 2
for r in data:
    ws.append(r)
    for col in range(1, 7):
        c = ws.cell(row=row_idx, column=col)
        c.alignment = left_align
        c.border = thin_border
    row_idx += 1

# Set columns width
ws.column_dimensions['A'].width = 5
ws.column_dimensions['B'].width = 15
ws.column_dimensions['C'].width = 30
ws.column_dimensions['D'].width = 40
ws.column_dimensions['E'].width = 40
ws.column_dimensions['F'].width = 25

# Add coloring for current version
for col in range(1, 7):
    ws.cell(row=6, column=col).fill = PatternFill(start_color="D9EAD3", end_color="D9EAD3", fill_type="solid")

wb.save(output_path)
print(f"Successfully written log to {output_path}")
