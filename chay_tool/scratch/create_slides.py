import os
import sys
import collections
import collections.abc
import math
from lxml import etree

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION
from pptx.chart.data import CategoryChartData

def set_shape_transparency(shape, alpha_percent):
    """Applies a custom XML transparency hack using lxml to set shape solid fill opacity."""
    shape.fill.solid()
    spPr = shape.element.spPr
    solidFill = spPr.find('{http://schemas.openxmlformats.org/drawingml/2006/main}solidFill')
    if solidFill is not None:
        color_element = solidFill.find('{http://schemas.openxmlformats.org/drawingml/2006/main}srgbClr')
        if color_element is None:
            color_element = solidFill.find('{http://schemas.openxmlformats.org/drawingml/2006/main}schemeClr')
        if color_element is not None:
            alpha_val = int(alpha_percent * 1000)
            # Remove any existing alpha elements
            for existing_alpha in color_element.findall('{http://schemas.openxmlformats.org/drawingml/2006/main}alpha'):
                color_element.remove(existing_alpha)
            # Add new alpha element
            alpha_el = etree.Element('{http://schemas.openxmlformats.org/drawingml/2006/main}alpha', val=str(alpha_val))
            color_element.append(alpha_el)

def create_presentation():
    print("Initiating 100% Native Vector PowerPoint Rebuild Pipeline...")
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    
    # ----------------------------------------------------
    # Color System & Constants
    # ----------------------------------------------------
    c_red = RGBColor(192, 0, 0)          # WinCommerce Main Red
    c_light_red = RGBColor(253, 233, 233) # Red Card Fill
    c_orange = RGBColor(237, 125, 49)    # WinCommerce Main Orange
    c_light_orange = RGBColor(255, 242, 230) # Orange Card Fill
    c_yellow = RGBColor(255, 192, 0)     # Warning Yellow
    c_blue = RGBColor(31, 78, 121)       # Corporate Navy Blue
    c_light_blue = RGBColor(235, 241, 245) # Navy Blue Card Fill
    c_green = RGBColor(56, 87, 35)       # Success Green
    c_light_green = RGBColor(240, 248, 240) # Green Card Fill
    c_purple = RGBColor(112, 48, 160)    # Action Purple
    c_light_purple = RGBColor(245, 235, 251) # Purple Card Fill
    c_dark_gray = RGBColor(40, 40, 40)   # Body Text Color
    c_light_gray = RGBColor(245, 245, 245) # Table Side Label Fill
    c_white = RGBColor(255, 255, 255)
    
    def apply_text_styling(paragraph, font_size=10, bold=False, color=c_dark_gray, align=PP_ALIGN.LEFT, italic=False):
        paragraph.alignment = align
        paragraph.font.name = "Segoe UI"
        paragraph.font.size = Pt(font_size)
        paragraph.font.bold = bold
        paragraph.font.italic = italic
        paragraph.font.color.rgb = color

    def add_header_footer(slide, title_text):
        """Creates the premium unified WinCommerce branding header & footer."""
        # Logo placeholder on Top-Left
        logo_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.2), Inches(3.5), Inches(0.6))
        tf = logo_box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = "Win"
        p.font.name = "Segoe UI"
        p.font.size = Pt(24)
        p.font.bold = True
        p.font.color.rgb = c_red
        
        run = p.add_run()
        run.text = "Commerce"
        run.font.name = "Segoe UI"
        run.font.size = Pt(24)
        run.font.bold = True
        run.font.color.rgb = RGBColor(120, 120, 120)
        
        # Sub-title
        p2 = tf.add_paragraph()
        p2.text = "MEMBER OF MASAN GROUP"
        p2.font.name = "Segoe UI"
        p2.font.size = Pt(6.5)
        p2.font.bold = True
        p2.font.color.rgb = RGBColor(160, 160, 160)
        p2.space_before = Pt(1)
        
        # Slide Title Capsule on Top-Right
        title_shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(5.5), Inches(0.2), Inches(7.333), Inches(0.55))
        title_shape.fill.solid()
        title_shape.fill.fore_color.rgb = c_red
        title_shape.line.color.rgb = c_red
        
        tf_title = title_shape.text_frame
        tf_title.word_wrap = True
        p_title = tf_title.paragraphs[0]
        p_title.text = title_text
        apply_text_styling(p_title, font_size=13, bold=True, color=c_white, align=PP_ALIGN.CENTER)
        
        # Subtle Bottom Accent Bars (Red & Orange)
        accent_red = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.5), Inches(7.15), Inches(8.0), Inches(0.06))
        accent_red.fill.solid()
        accent_red.fill.fore_color.rgb = c_red
        accent_red.line.fill.background()
        
        accent_orange = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(8.5), Inches(7.15), Inches(4.333), Inches(0.06))
        accent_orange.fill.solid()
        accent_orange.fill.fore_color.rgb = c_orange
        accent_orange.line.fill.background()
        
        # Footer
        footer_box = slide.shapes.add_textbox(Inches(0.5), Inches(7.22), Inches(12.333), Inches(0.25))
        tf_foot = footer_box.text_frame
        p_foot = tf_foot.paragraphs[0]
        p_foot.text = "WinCommerce © 2026  |  Tài liệu Vận hành Nội bộ  |  Bảo mật tuyệt đối"
        apply_text_styling(p_foot, font_size=7.5, color=RGBColor(150, 150, 150))

    slide_layout = prs.slide_layouts[6] # Blank slide layout

    # =========================================================================
    # SLIDE 1: Tình hình XLVP tại WCM (6 Native Charts)
    # =========================================================================
    print("Building Slide 1: Overview & 6 Native Charts...")
    slide1 = prs.slides.add_slide(slide_layout)
    add_header_footer(slide1, "TÌNH HÌNH XỬ LÝ VI PHẠM (XLVP) TẠI WCM TRONG THỜI GIAN QUA")
    
    # Subtitle Stat Pill
    stat_shape = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.5), Inches(0.95), Inches(12.333), Inches(0.4))
    stat_shape.fill.solid()
    stat_shape.fill.fore_color.rgb = c_light_red
    stat_shape.line.color.rgb = c_red
    tf_stat = stat_shape.text_frame
    p_stat = tf_stat.paragraphs[0]
    p_stat.text = "📝 Tổng số biên bản tính từ năm 2025 – T5/2026:  20,659 biên bản  (trung bình ~1,300 BB/tháng)"
    apply_text_styling(p_stat, font_size=11, bold=True, color=c_red, align=PP_ALIGN.CENTER)
    
    # Define Grid for 6 Charts: 2 rows x 3 columns
    # Row 1: Y = 1.8, Row 2: Y = 4.45
    # Col 1: X = 0.5, Col 2: X = 4.75, Col 3: X = 9.0
    # Size: width 3.833, height 2.3
    
    grid = [
        {"x": Inches(0.5), "y": Inches(1.5), "title": "Thâm niên của CBNV vi phạm"},
        {"x": Inches(4.75), "y": Inches(1.5), "title": "Số lượng vi phạm theo cấp bậc"},
        {"x": Inches(9.0), "y": Inches(1.5), "title": "Số lượng XLVP theo chuỗi"},
        {"x": Inches(0.5), "y": Inches(4.35), "title": "Số lượng vi phạm theo nhóm lỗi"},
        {"x": Inches(4.75), "y": Inches(4.35), "title": "Chi tiết lỗi nhóm 1 (Hàng hóa)"},
        {"x": Inches(9.0), "y": Inches(4.35), "title": "Chi tiết lỗi nhóm 2 (Tài chính)"}
    ]
    
    for i, g in enumerate(grid):
        # White background card container
        card = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, g["x"], g["y"], Inches(3.833), Inches(2.65))
        card.fill.solid()
        card.fill.fore_color.rgb = c_white
        card.line.color.rgb = RGBColor(220, 220, 220)
        
        # Card title
        t_box = slide1.shapes.add_textbox(g["x"], g["y"] + Inches(0.05), Inches(3.833), Inches(0.35))
        p_t = t_box.text_frame.paragraphs[0]
        p_t.text = g["title"]
        apply_text_styling(p_t, font_size=9.5, bold=True, color=c_red, align=PP_ALIGN.CENTER)
        
        # Add Native Chart
        chart_data = CategoryChartData()
        if i == 0:
            chart_data.categories = ['< 1 năm', '1-3 năm', '3-5 năm', '> 5 năm']
            chart_data.add_series('Tỷ lệ', (0.42, 0.35, 0.15, 0.08))
            chart_type = XL_CHART_TYPE.COLUMN_CLUSTERED
        elif i == 1:
            chart_data.categories = ['Nhân viên', 'T.Nhóm', 'Cửa hàng', 'Khác']
            chart_data.add_series('Số lượng', (12500, 4800, 2600, 759))
            chart_type = XL_CHART_TYPE.COLUMN_CLUSTERED
        elif i == 2:
            chart_data.categories = ['WinMart+', 'WinMart', 'Khác']
            chart_data.add_series('Tỷ lệ', (0.68, 0.25, 0.07))
            chart_type = XL_CHART_TYPE.PIE
        elif i == 3:
            chart_data.categories = ['Hàng hóa', 'Vận hành', 'Tài chính', 'Khác']
            chart_data.add_series('Số lượng', (8900, 6200, 4300, 1259))
            chart_type = XL_CHART_TYPE.COLUMN_CLUSTERED
        elif i == 4:
            chart_data.categories = ['Tồn ảo', 'Hủy khống', 'Date lỗi', 'Khác']
            chart_data.add_series('Tỷ lệ', (0.45, 0.28, 0.18, 0.09))
            chart_type = XL_CHART_TYPE.PIE
        else:
            chart_data.categories = ['Gian lận DT', 'Coupon khống', 'Ém tiền', 'Khác']
            chart_data.add_series('Số lượng', (1800, 1200, 900, 400))
            chart_type = XL_CHART_TYPE.BAR_CLUSTERED
            
        x_c = g["x"] + Inches(0.15)
        y_c = g["y"] + Inches(0.4)
        w_c = Inches(3.533)
        h_c = Inches(2.1)
        
        chart = slide1.shapes.add_chart(chart_type, x_c, y_c, w_c, h_c, chart_data).chart
        chart.has_legend = (chart_type == XL_CHART_TYPE.PIE)
        if chart.has_legend:
            chart.legend.position = XL_LEGEND_POSITION.RIGHT
            chart.legend.font.name = "Segoe UI"
            chart.legend.font.size = Pt(7.5)
            
        # Format axes
        if chart_type in [XL_CHART_TYPE.COLUMN_CLUSTERED, XL_CHART_TYPE.BAR_CLUSTERED]:
            chart.value_axis.has_major_gridlines = False
            chart.value_axis.tick_labels.font.name = "Segoe UI"
            chart.value_axis.tick_labels.font.size = Pt(7.5)
            chart.category_axis.tick_labels.font.name = "Segoe UI"
            chart.category_axis.tick_labels.font.size = Pt(7.5)

    # =========================================================================
    # SLIDE 2: VẤN ĐỀ CỦA HỆ THỐNG MINIMART HIỆN NAY (4 Columns)
    # =========================================================================
    print("Building Slide 2: 4 Columns...")
    slide2 = prs.slides.add_slide(slide_layout)
    add_header_footer(slide2, "VẤN ĐỀ CỦA HỆ THỐNG MINIMART HIỆN NAY (1/3)")
    
    col_w = Inches(2.9)
    col_h = Inches(5.6)
    gap = Inches(0.244)
    y_start = Inches(1.3)
    
    columns_data = [
        {
            "header": "● 1 ●\nHệ thống kiểm soát đang chạy theo sự vụ",
            "bg_color": c_light_red,
            "header_color": c_red,
            "bullets": [
                "Quá tập trung vào vấn đề để xử lý khi có thất thoát xảy ra mà không có cảnh báo sớm",
                "Chưa có hệ thống chấm điểm rủi ro cửa hàng hiệu quả",
                "=> KSTT luôn đi sau vi phạm"
            ]
        },
        {
            "header": "● 2 ●\nVận hành không thực sự chủ động",
            "bg_color": c_light_orange,
            "header_color": c_orange,
            "bullets": [
                "Quản lý khu vực che cho cửa hàng",
                "Quản lý cửa hàng che cho nhân viên",
                "Báo cáo nội bộ luôn làm đẹp số liệu",
                "Cùng một hệ thống tự kiểm tra lẫn nhau",
                "=> \"người phạm lỗi cũng là người báo cáo lỗi\""
            ]
        },
        {
            "header": "● 3 ●\nNhân sự ra vào nhiều, việc đào tạo chưa thực sự ngấm vào CBNV",
            "bg_color": c_light_green,
            "header_color": c_green,
            "bullets": [
                "Nhân sự mới không hiểu quy định",
                "Nhân sự nghỉ liên tục làm đứt gãy kiểm soát",
                "Người cũ truyền thông sai văn hóa cho người mới",
                "=> sai phạm trở thành \"thói quen vận hành\""
            ]
        },
        {
            "header": "● 4 ●\nSuy nghĩ làm đủ mọi cách \"miễn đạt doanh số là được\" cần thay đổi",
            "bg_color": c_light_purple,
            "header_color": c_purple,
            "bullets": [
                "Suy nghĩ làm đủ mọi cách \"miễn đạt doanh số là được\" ăn sâu vào thói quen vận hành.",
                "Cần phải thay đổi quyết liệt thành tư duy: \"Đạt doanh số bằng cách đúng luật\""
            ]
        }
    ]
    
    for idx, col in enumerate(columns_data):
        x_pos = Inches(0.5) + idx * (col_w + gap)
        
        # Header Capsule
        h_shape = slide2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x_pos, y_start, col_w, Inches(1.1))
        h_shape.fill.solid()
        h_shape.fill.fore_color.rgb = col["header_color"]
        h_shape.line.color.rgb = col["header_color"]
        tf_h = h_shape.text_frame
        tf_h.word_wrap = True
        p_h = tf_h.paragraphs[0]
        p_h.text = col["header"]
        apply_text_styling(p_h, font_size=9, bold=True, color=c_white, align=PP_ALIGN.CENTER)
        
        # Body Card
        b_shape = slide2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x_pos, y_start + Inches(1.2), col_w, col_h - Inches(1.2))
        b_shape.fill.solid()
        b_shape.fill.fore_color.rgb = col["bg_color"]
        b_shape.line.color.rgb = col["header_color"]
        
        tf_b = b_shape.text_frame
        tf_b.word_wrap = True
        tf_b.margin_left = tf_b.margin_right = Inches(0.15)
        tf_b.margin_top = Inches(0.15)
        
        for i_b, bullet in enumerate(col["bullets"]):
            p_b = tf_b.paragraphs[0] if i_b == 0 else tf_b.add_paragraph()
            p_b.text = "• " + bullet
            apply_text_styling(p_b, font_size=8.5, color=c_dark_gray)
            p_b.space_before = Pt(6)
            if "=>" in bullet or "đúng luật" in bullet:
                p_b.font.bold = True
                p_b.font.color.rgb = col["header_color"]

    # =========================================================================
    # SLIDE 3: VẤN ĐỀ CỦA HỆ THỐNG MINIMART HIỆN NAY (2/3) - NGUYÊN NHÂN & HỆ QUẢ
    # =========================================================================
    print("Building Slide 3: Causes & Consequences Table...")
    slide3_new = prs.slides.add_slide(slide_layout)
    add_header_footer(slide3_new, "VẤN ĐỀ CỦA HỆ THỐNG MINIMART HIỆN NAY (2/3) - NGUYÊN NHÂN & HỆ QUẢ")
    
    # Storefront Image
    store_img_path = "scratch/cropped_storefront.jpg"
    if os.path.exists(store_img_path):
        slide3_new.shapes.add_picture(store_img_path, Inches(1.1), Inches(2.9), Inches(2.6), Inches(2.2))
    
    # Semicircular connector line
    orbit = slide3_new.shapes.add_shape(MSO_SHAPE.OVAL, Inches(0.7), Inches(2.3), Inches(3.4), Inches(3.4))
    orbit.fill.background()
    orbit.line.color.rgb = c_red
    orbit.line.width = Pt(1.5)
    orbit.line.dash_style = 2  # dashed line
    
    # Push orbit back in Z-order
    slide3_new.shapes._spTree.remove(orbit._element)
    slide3_new.shapes._spTree.insert(2, orbit._element)
    
    # 5 Semicircle circular cards
    xc = 2.4
    yc = 4.0
    R = 1.7
    cw = 0.95
    ch = 0.95
    
    points_data = [
        {"num": "01", "angle": -90, "text": "Quá tải\ncông việc", "fs": 8},
        {"num": "02", "angle": -25, "text": "Thiếu nhân sự &\nđào tạo chưa\nhiệu quả", "fs": 6.8},
        {"num": "03", "angle": 35, "text": "Hạ tầng &\nthiết bị\nxuống cấp", "fs": 7.2},
        {"num": "04", "angle": 95, "text": "Chất lượng\nhàng hóa", "fs": 8},
        {"num": "05", "angle": 155, "text": "Khuyến mại &\nhoạt náo\nbán hàng", "fs": 7}
    ]
    
    for pt in points_data:
        rad = pt["angle"] * (math.pi / 180.0)
        px = xc + R * math.cos(rad)
        py = yc + R * math.sin(rad)
        
        # White base circle
        c_shape = slide3_new.shapes.add_shape(MSO_SHAPE.OVAL, Inches(px - cw/2), Inches(py - ch/2), Inches(cw), Inches(ch))
        c_shape.fill.solid()
        c_shape.fill.fore_color.rgb = c_white
        c_shape.line.color.rgb = c_red
        c_shape.line.width = Pt(1.5)
        
        tf_c = c_shape.text_frame
        tf_c.word_wrap = True
        tf_c.margin_left = tf_c.margin_right = Inches(0.04)
        tf_c.margin_top = Inches(0.12)
        p_c = tf_c.paragraphs[0]
        p_c.text = pt["text"]
        apply_text_styling(p_c, font_size=pt["fs"], bold=True, color=c_dark_gray, align=PP_ALIGN.CENTER)
        
        # Red index pill overlapping top of circle
        pw = 0.36
        ph = 0.36
        pill = slide3_new.shapes.add_shape(MSO_SHAPE.OVAL, Inches(px - pw/2), Inches(py - ch/2 - ph/3), Inches(pw), Inches(ph))
        pill.fill.solid()
        pill.fill.fore_color.rgb = c_red
        pill.line.color.rgb = c_red
        tf_p = pill.text_frame
        p_p = tf_p.paragraphs[0]
        p_p.text = pt["num"]
        apply_text_styling(p_p, font_size=7.5, bold=True, color=c_white, align=PP_ALIGN.CENTER)
        
    # Right Side: Causes & Consequences Table
    rows = 6
    cols = 4
    t_shape = slide3_new.shapes.add_table(rows, cols, Inches(4.8), Inches(1.35), Inches(8.033), Inches(5.3))
    tbl_new = t_shape.table
    
    tbl_new.columns[0].width = Inches(0.35)
    tbl_new.columns[1].width = Inches(2.15)
    tbl_new.columns[2].width = Inches(2.766)
    tbl_new.columns[3].width = Inches(2.766)
    
    headers_new = [
        "",
        "👥  Nhóm nguyên nhân",
        "🔍  Biểu hiện chính",
        "⚠️  Hệ quả"
    ]
    
    for c_idx, text in enumerate(headers_new):
        cell = tbl_new.cell(0, c_idx)
        cell.fill.solid()
        if c_idx < 2:
            cell.fill.fore_color.rgb = c_red
            p = cell.text_frame.paragraphs[0]
            p.text = text
            apply_text_styling(p, font_size=10, bold=True, color=c_white, align=PP_ALIGN.CENTER)
        else:
            cell.fill.fore_color.rgb = c_light_red
            p = cell.text_frame.paragraphs[0]
            p.text = text
            apply_text_styling(p, font_size=10, bold=True, color=c_red, align=PP_ALIGN.CENTER)
            
    table_act_data_new = [
        (
            "1",
            "💼  Quá tải\ncông việc",
            [
                "• CHT kiêm nhiệm nhiều CH, thường xuyên hỗ trợ khai trương",
                "• QLKV quản lý địa bàn rộng",
                "• Thiếu giám sát trực tiếp tại CH"
            ],
            [
                "• Hủy dòng, trả hàng, hủy bill tăng cao",
                "• Mất kiểm soát tại cửa hàng"
            ]
        ),
        (
            "2",
            "👥  Thiếu nhân sự &\nđào tạo chưa\nhiệu quả",
            [
                "• Nhân viên phải làm 2 ca trong nhiều ngày",
                "• Nhân sự mới/ CHT mới chưa nắm nghiệp vụ",
                "• Quy trình thay đổi"
            ],
            [
                "• Sai nhập kho, sai kiểm kê, sai hủy hàng"
            ]
        ),
        (
            "3",
            "🔧  Hạ tầng &\nthiết bị xuống cấp",
            [
                "• Chuột, côn trùng",
                "• Tủ mát, điều hòa xuống cấp",
                "• POS thanh toán treo/ lỗi không nhận barcode",
                "• Hệ thống đồng bộ giá chậm"
            ],
            [
                "• Hỏng hủy thất thoát tăng cao",
                "• Khó kiểm soát gian lận"
            ]
        ),
        (
            "4",
            "📦  Chất lượng\nhàng hóa",
            [
                "• CLSP khi được giao không tốt",
                "• Nhân viên không đủ thời gian lọc lựa"
            ],
            [
                "• Tăng mạnh tỷ lệ hỏng hủy thực tế"
            ]
        ),
        (
            "5",
            "🏷️  Khuyến mại &\nhoạt náo bán hàng",
            [
                "• CTKM thay đổi liên tục",
                "• Hoạt náo, coupon/voucher khó kiểm soát tồn"
            ],
            [
                "• Gian lận, thất thoát, sai lệch kiểm kê tăng cao"
            ]
        )
    ]
    
    for r_idx, row in enumerate(table_act_data_new):
        cell_idx = tbl_new.cell(r_idx + 1, 0)
        cell_idx.fill.solid()
        cell_idx.fill.fore_color.rgb = c_light_gray
        p_idx = cell_idx.text_frame.paragraphs[0]
        p_idx.text = row[0]
        apply_text_styling(p_idx, font_size=9, bold=True, color=c_blue, align=PP_ALIGN.CENTER)
        
        cell_name = tbl_new.cell(r_idx + 1, 1)
        cell_name.fill.solid()
        cell_name.fill.fore_color.rgb = c_light_gray
        p_name = cell_name.text_frame.paragraphs[0]
        p_name.text = row[1]
        apply_text_styling(p_name, font_size=8.5, bold=True, color=c_red, align=PP_ALIGN.CENTER)
        
        cell_manifest = tbl_new.cell(r_idx + 1, 2)
        cell_manifest.fill.solid()
        cell_manifest.fill.fore_color.rgb = c_white
        tf_manifest = cell_manifest.text_frame
        tf_manifest.word_wrap = True
        for i_m, line in enumerate(row[2]):
            p = tf_manifest.paragraphs[0] if i_m == 0 else tf_manifest.add_paragraph()
            p.text = line
            apply_text_styling(p, font_size=7.5, color=c_dark_gray)
            p.space_before = Pt(2)
            
        cell_conseq = tbl_new.cell(r_idx + 1, 3)
        cell_conseq.fill.solid()
        cell_conseq.fill.fore_color.rgb = c_white
        tf_conseq = cell_conseq.text_frame
        tf_conseq.word_wrap = True
        for i_c, line in enumerate(row[3]):
            p = tf_conseq.paragraphs[0] if i_c == 0 else tf_conseq.add_paragraph()
            p.text = line
            apply_text_styling(p, font_size=7.5, color=c_dark_gray)
            p.space_before = Pt(2)

    # =========================================================================
    # SLIDE 4: VẤN ĐỀ CỦA HỆ THỐNG MINIMART HIỆN NAY (3/3) - 10 HÀNH VI NGUY CƠ GIAN LẬN
    # =========================================================================
    print("Building Slide 4: 10 Circular Store Risks...")
    slide3 = prs.slides.add_slide(slide_layout)
    add_header_footer(slide3, "VẤN ĐỀ CỦA HỆ THỐNG MINIMART HIỆN NAY (3/3) - 10 HÀNH VI NGUY CƠ GIAN LẬN")
    
    # Center Point of Slide
    cx = 6.666
    cy = 4.15
    
    # 1. Central Storefront Shape (House/Store representation)
    store = slide3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(cx - 1.1), Inches(cy - 0.75), Inches(2.2), Inches(1.5))
    store.fill.solid()
    store.fill.fore_color.rgb = c_red
    store.line.color.rgb = c_orange
    store.line.width = Pt(3)
    tf_store = store.text_frame
    p_store = tf_store.paragraphs[0]
    p_store.text = "🏪\nCỬA HÀNG\nWINMART+"
    apply_text_styling(p_store, font_size=11, bold=True, color=c_white, align=PP_ALIGN.CENTER)
    
    # 2. Arrange 10 Risk Cards in a beautiful circle
    radius_x = 4.45
    radius_y = 2.45
    
    risks = [
        {"title": "Bán hàng SLL không qua POS", "severity": "RẤT CAO", "color": c_red},
        {"title": "Hủy dòng / Hủy giao dịch trục lợi", "severity": "RẤT CAO", "color": c_red},
        {"title": "Quay vòng DT / Không vào DT", "severity": "RẤT CAO", "color": c_red},
        {"title": "Gian lận số liệu Kiểm kê khống", "severity": "CAO", "color": c_orange},
        {"title": "STO/PO treo tạo/hủy khống", "severity": "CAO", "color": c_orange},
        {"title": "Gian lận Coupon / Voucher", "severity": "CAO", "color": c_orange},
        {"title": "Không nhập Hàng KM lên hệ thống", "severity": "CAO", "color": c_orange},
        {"title": "Ém hủy / Hủy sai thực tế", "severity": "TRUNG BÌNH", "color": c_yellow},
        {"title": "Gian lận CT hội viên", "severity": "TRUNG BÌNH", "color": c_yellow},
        {"title": "Công ca bất thường", "severity": "TRUNG BÌNH", "color": c_yellow}
    ]
    
    for i, r in enumerate(risks):
        angle = i * (360.0 / 10.0) * (math.pi / 180.0)
        px = cx + radius_x * math.cos(angle)
        py = cy + radius_y * math.sin(angle)
        
        # Dimensions of each card
        cw = 1.9
        ch = 0.95
        
        card = slide3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(px - cw/2), Inches(py - ch/2), Inches(cw), Inches(ch))
        card.fill.solid()
        card.fill.fore_color.rgb = c_white
        card.line.color.rgb = r["color"]
        card.line.width = Pt(1.5)
        
        # Add Connecting Line
        connector = slide3.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(cx), Inches(cy), Inches(px), Inches(py))
        connector.line.color.rgb = RGBColor(220, 220, 220)
        connector.line.width = Pt(1)
        # Push connector back in Z-order using python-pptx shape ordering
        slide3.shapes._spTree.remove(connector._element)
        slide3.shapes._spTree.insert(2, connector._element)
        
        # Text frame inside card
        tf_c = card.text_frame
        tf_c.word_wrap = True
        tf_c.margin_left = tf_c.margin_right = Inches(0.08)
        tf_c.margin_top = Inches(0.08)
        
        # Risk Index & Severity Tag
        p_c1 = tf_c.paragraphs[0]
        p_c1.text = f"🚨 Nguy cơ {i+1:02d}"
        apply_text_styling(p_c1, font_size=7.5, bold=True, color=r["color"])
        
        # Title text
        p_c2 = tf_c.add_paragraph()
        p_c2.text = r["title"]
        apply_text_styling(p_c2, font_size=8, bold=True, color=c_dark_gray)
        p_c2.space_before = Pt(2)
        
        # Severity pill
        p_c3 = tf_c.add_paragraph()
        p_c3.text = f"Mức độ: {r['severity']}"
        apply_text_styling(p_c3, font_size=7, bold=True, color=r["color"])
        p_c3.space_before = Pt(1)

    # Re-insert store shape to make sure it's on top of lines
    slide3.shapes._spTree.remove(store._element)
    slide3.shapes._spTree.append(store._element)

    # =========================================================================
    # SLIDE 5: Hoạt động trọng tâm 2026 (Circles)
    # =========================================================================
    print("Building Slide 5: Overlapping Circles centerpiece...")
    slide4 = prs.slides.add_slide(slide_layout)
    add_header_footer(slide4, "HOẠT ĐỘNG TRỌNG TÂM NĂM 2026")
    
    # 3 Overlapping Circles centerpiece
    # Layout dimensions
    ccx = 6.666
    ccy = 3.65
    cw = Inches(2.5)
    ch = Inches(2.5)
    
    # Circle 1 (Red)
    circle1 = slide4.shapes.add_shape(MSO_SHAPE.OVAL, Inches(ccx - 1.25), Inches(ccy - 1.8), cw, ch)
    circle1.fill.solid()
    circle1.fill.fore_color.rgb = c_red
    circle1.line.color.rgb = c_red
    set_shape_transparency(circle1, 70)
    tf1 = circle1.text_frame
    tf1.word_wrap = True
    p1 = tf1.paragraphs[0]
    p1.text = "\n\n01\nPhòng chống\ngian lận thất thoát"
    apply_text_styling(p1, font_size=9, bold=True, color=c_white, align=PP_ALIGN.CENTER)
    
    # Circle 2 (Yellow)
    circle2 = slide4.shapes.add_shape(MSO_SHAPE.OVAL, Inches(ccx - 0.1), Inches(ccy - 0.2), cw, ch)
    circle2.fill.solid()
    circle2.fill.fore_color.rgb = c_yellow
    circle2.line.color.rgb = c_yellow
    set_shape_transparency(circle2, 70)
    tf2 = circle2.text_frame
    tf2.word_wrap = True
    p2 = tf2.paragraphs[0]
    p2.text = "\n\n02\nĐảm bảo\nCLKK"
    apply_text_styling(p2, font_size=9, bold=True, color=c_dark_gray, align=PP_ALIGN.CENTER)
    
    # Circle 3 (Blue)
    circle3 = slide4.shapes.add_shape(MSO_SHAPE.OVAL, Inches(ccx - 2.4), Inches(ccy - 0.2), cw, ch)
    circle3.fill.solid()
    circle3.fill.fore_color.rgb = c_blue
    circle3.line.color.rgb = c_blue
    set_shape_transparency(circle3, 70)
    tf3 = circle3.text_frame
    tf3.word_wrap = True
    p3 = tf3.paragraphs[0]
    p3.text = "\n\n03\nTuân thủ\nQT/QĐ"
    apply_text_styling(p3, font_size=9, bold=True, color=c_white, align=PP_ALIGN.CENTER)
    
    # 6 Surrounding blocks
    surrounds = [
        {"x": Inches(0.5), "y": Inches(1.3), "title": "🎯  Trọng tâm", "bullets": ["Rủi ro trọng yếu: Gian lận trong lọc lạm dụng chính sách, thất thoát tài sản.", "Ưu tiên nguồn lực theo mục tiêu ảnh hưởng và tần suất rủi ro"]},
        {"x": Inches(0.5), "y": Inches(3.05), "title": "📢  Thông minh", "bullets": ["Chuẩn hóa các chỉ số rủi ro và logic điều kiện", "Hệ thống hóa thành bản cẩm nang – trên mỗi cửa sổ rủi ro: CBLĐ vận hành kiểm tra nhanh hơn"]},
        {"x": Inches(1.8), "y": Inches(4.95), "title": "⚙️  VH chủ động", "bullets": ["Tự thanh kiểm tra và chủ động xử lý vi phạm QT / đơn giản", "Đưa phát hiện sai vào xu hướng kỳ KSYT với ưu việt nhắc nhở"]},
        {"x": Inches(9.0), "y": Inches(1.3), "title": "📈  Tần suất tối ưu", "bullets": ["Xuất hiện từ điểm ngưỡng rủi ro, hài hòa nguồn lực để VH luôn trọng tâm để giảm mức độ kiểm tra để duy trì áp lực tuân thủ"]},
        {"x": Inches(9.0), "y": Inches(3.05), "title": "🎯  Mục tiêu cụ thể", "bullets": ["Cải thiện thông qua lịch sử, phân tích.", "Đo lường dựa trên tỷ lệ phát hiện sai phạm và mức thất thoát."]},
        {"x": Inches(7.7), "y": Inches(4.95), "title": "🔍  KSTT giám sát", "bullets": ["Thẩm quyền / khoanh vùng rủi ro lớn để đảm bảo chính xác khách quan", "Tăng tuân thủ răn đe và tuân thủ hệ thống"]}
    ]
    
    for s in surrounds:
        card = slide4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, s["x"], s["y"], Inches(3.8), Inches(1.55))
        card.fill.solid()
        card.fill.fore_color.rgb = c_white
        card.line.color.rgb = RGBColor(220, 220, 220)
        card.line.width = Pt(1.5)
        
        tf_s = card.text_frame
        tf_s.word_wrap = True
        tf_s.margin_left = tf_s.margin_right = Inches(0.12)
        tf_s.margin_top = Inches(0.1)
        
        p_t = tf_s.paragraphs[0]
        p_t.text = s["title"]
        apply_text_styling(p_t, font_size=10.5, bold=True, color=c_red)
        
        for bullet in s["bullets"]:
            p_b = tf_s.add_paragraph()
            p_b.text = "• " + bullet
            apply_text_styling(p_b, font_size=8.2, color=c_dark_gray)
            p_b.space_before = Pt(4)

    # =========================================================================
    # SLIDE 6: Phương án kiểm soát, giám sát (Matrix Table)
    # =========================================================================
    print("Building Slide 6: Matrix Table...")
    slide5 = prs.slides.add_slide(slide_layout)
    add_header_footer(slide5, "PHƯƠNG ÁN KIỂM SOÁT, GIÁM SÁT CỬA HÀNG NĂM 2026")
    
    # Subtitle Subhead
    sub_box = slide5.shapes.add_textbox(Inches(0.5), Inches(0.95), Inches(12.333), Inches(0.35))
    p_sub = sub_box.text_frame.paragraphs[0]
    p_sub.text = "💡 Dữ liệu thông suốt, rà soát liên tục để phát hiện kịp thời nguy cơ sai phạm tại hệ thống minimart"
    apply_text_styling(p_sub, font_size=11, bold=True, color=c_dark_gray, italic=True)
    
    # Matrix Table using PowerPoint Native Table
    rows = 6
    cols = 3
    t_shape = slide5.shapes.add_table(rows, cols, Inches(0.5), Inches(1.35), Inches(12.333), Inches(4.7))
    tbl = t_shape.table
    
    # Column widths
    tbl.columns[0].width = Inches(2.2)
    tbl.columns[1].width = Inches(5.066)
    tbl.columns[2].width = Inches(5.066)
    
    headers = [
        "👥  Nhóm nguy cơ",
        "🎯 GSKK\n(Kiểm kê dựa trên chỉ số rủi ro)",
        "🔍 KSTT\n(Xác minh dựa trên tín hiệu bất thường)"
    ]
    for c_idx, text in enumerate(headers):
        cell = tbl.cell(0, c_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = c_red if c_idx == 0 else c_light_red
        
        p = cell.text_frame.paragraphs[0]
        p.text = text
        apply_text_styling(p, font_size=10.5, bold=True, color=c_white if c_idx == 0 else c_red, align=PP_ALIGN.CENTER)
        
    table_data = [
        (
            "💰 Tồn cao/\ntồn ảo",
            ["✔ Chỉ số DIO chung của CH", "✔ Tỷ lệ giá trị hàng no sale trên doanh thu CH, DIO, Stock Qty/Sale Qty bình quân 30 ngày."],
            ["✔ Tập trung theo mã hot sale có tồn cao nhưng không sale trong tháng (trên 7-14 ngày)", "✔ Các mã slow moving non - sale đặc biệt thuộc ngành hàng FS, top sale, giá trị lớn"]
        ),
        (
            "📈 Gian lận\ntrục lợi",
            ["✔ Giá trị và tỷ lệ giá trị hủy đơn trên doanh thu", "✔ Giá trị và tỷ lệ trả hàng trên doanh thu"],
            ["✔ Các giao dịch hủy đơn trả hàng bất thường (thường vào ngày cuối tháng, sau mốc chốt doanh số)", "✔ Các mặt hàng hủy không liên quan đến chương trình khuyến mại, tích điểm, ưu đãi, hoa hồng"]
        ),
        (
            "🗄️ Gian lận\nsố liệu",
            ["✔ Giá trị và tỷ lệ hủy hàng trên doanh thu", "✔ Giá trị và tỷ lệ thất thoát trên doanh thu", "✔ Giá trị và tỷ lệ chuyển giao trên doanh thu", "✔ Giá trị chênh lệch định mức"],
            ["✔ Doanh thu bất thường vào các thời điểm nhạy cảm: cuối tháng, vào các ngày khuyến mại", "✔ Giá trị chậm giao/đổi hàng bất thường so với số lượng trung bình", "✔ Giá trị hủy hàng, kiểm kê bất thường so với số lượng bình quân (SP không hủy/lỗi vẫn bán đi), XK sp cần kỹ lượng có check (cctv)"]
        ),
        (
            "💼 Lỗi nghiệp\nvụ",
            ["✔ Tỷ lệ giá trị coupon cao do nghiệp vụ quản lý kém", "✔ Tỷ lệ nghiệp vụ đặt thừa cao (hủy, thiếu, nhập kho, xuất trả NCC...)", "✔ Tận dụng STO treo"],
            ["✔ Các giao dịch hủy phiếu nhập kho nhưng không có giao dịch nhập kho đi kèm", "✔ Giao dịch không nhập bằng KM 0đ", "✔ So sánh doanh thu hàng tương đương"]
        ),
        (
            "👥 Các nhóm\nkhác",
            ["✔ Doanh thu < Chi phí 3 tháng liên tiếp", "✔ Tình trạng kiểm kê, tuân thủ tối thiểu TRK 1 lần/năm", "✔ Mùa luân chuyển đảm bảo sau luân chuyển 1 đến 2 tháng sẽ thực hiện TRK"],
            ["✔ Dữ liệu điểm cộng bất thường", "✔ Giá trị tồn ảo cao", "✔ Các khách hàng có tổng giá trị thanh toán cao đột biến"]
        )
    ]
    
    for r_idx, row in enumerate(table_data):
        for c_idx, data in enumerate(row):
            cell = tbl.cell(r_idx + 1, c_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = c_light_gray if c_idx == 0 else c_white
            
            tf = cell.text_frame
            tf.word_wrap = True
            
            if c_idx == 0:
                p = tf.paragraphs[0]
                p.text = data
                apply_text_styling(p, font_size=10, bold=True, color=c_dark_gray, align=PP_ALIGN.CENTER)
            else:
                for idx, line in enumerate(data):
                    p = tf.paragraphs[0] if idx == 0 else tf.add_paragraph()
                    p.text = line
                    apply_text_styling(p, font_size=8, color=c_dark_gray)
                    p.space_before = Pt(3)

    # 4 Status Banner Cards below the table
    banner_y = Inches(6.1)
    banner_w = Inches(2.9)
    banner_gap = Inches(0.244)
    
    status_data = [
        {"text": "📊 Giám sát toàn diện\nTheo dõi liên tục các chỉ số rủi ro, phát hiện sớm bất thường", "bg": c_red, "text_color": c_white},
        {"text": "🔔 Cảnh báo kịp thời\nHệ thống cảnh báo tự động khi vượt ngưỡng rủi ro", "bg": c_light_orange, "text_color": c_orange},
        {"text": "🛡️ Xác minh chính xác\nĐi sâu phân tích theo tín hiệu, khoanh vùng đúng trọng điểm", "bg": c_light_green, "text_color": c_green},
        {"text": "📑 Hành động hiệu quả\nĐưa ra giải pháp, xử lý kịp thời, ngăn ngừa tái diễn", "bg": c_blue, "text_color": c_white}
    ]
    
    for idx, status in enumerate(status_data):
        s_pos = Inches(0.5) + idx * (banner_w + banner_gap)
        card = slide5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, s_pos, banner_y, banner_w, Inches(0.7))
        card.fill.solid()
        card.fill.fore_color.rgb = status["bg"]
        card.line.color.rgb = status["bg"]
        tf_s = card.text_frame
        tf_s.word_wrap = True
        tf_s.margin_left = tf_s.margin_right = Inches(0.08)
        p_s = tf_s.paragraphs[0]
        p_s.text = status["text"]
        apply_text_styling(p_s, font_size=7.5, bold=True, color=status["text_color"], align=PP_ALIGN.CENTER)

    # =========================================================================
    # SLIDE 7: So sánh phương án kiểm tra các CH
    # =========================================================================
    print("Building Slide 7: Comparison & Flowchart Steps...")
    slide6 = prs.slides.add_slide(slide_layout)
    add_header_footer(slide6, "SO SÁNH PHƯƠNG ÁN KIỂM TRA CÁC CỬA HÀNG")
    
    # Subtitle
    sub_box = slide6.shapes.add_textbox(Inches(0.5), Inches(0.95), Inches(12.333), Inches(0.35))
    p_sub = sub_box.text_frame.paragraphs[0]
    p_sub.text = "💡 Lựa chọn phương án tối ưu dựa trên phân tích rủi ro và tăng cường tính hiện diện"
    apply_text_styling(p_sub, font_size=11, bold=True, color=c_dark_gray, italic=True)
    
    # Table Comparison
    t_shape = slide6.shapes.add_table(5, 3, Inches(0.5), Inches(1.35), Inches(12.333), Inches(4.1))
    tbl_comp = t_shape.table
    
    tbl_comp.columns[0].width = Inches(2.2)
    tbl_comp.columns[1].width = Inches(5.066)
    tbl_comp.columns[2].width = Inches(5.066)
    
    # Headers
    headers = ["🔎  Tiêu chí", "📋  Phương pháp hiện tại", "🎯  Phương pháp dự kiến"]
    for c_idx, text in enumerate(headers):
        cell = tbl_comp.cell(0, c_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = c_red if c_idx == 0 or c_idx == 1 else c_light_red
        p = cell.text_frame.paragraphs[0]
        p.text = text
        apply_text_styling(p, font_size=10.5, bold=True, color=c_white if c_idx < 2 else c_red, align=PP_ALIGN.CENTER)
        
    comp_data = [
        (
            "👥 Đối tượng\nkiểm tra",
            ["› Tập trung theo cấp quản lý: QLKV, GĐV để có thể đánh giá tổng quan năng lực quản lý của khu vực.", "› Từ đó nêu được trách nhiệm liên đới và khắc phục của cấp quản lý."],
            ["✔ Tập trung vào CH có nguy cơ gian lận sai phạm thông qua phân tích số liệu.", "✔ Phân bổ để tối ưu độ phủ với mục tiêu tối đa các khu vực có CH được kiểm tra"]
        ),
        (
            "🔍 Cách lựa chọn",
            ["› Phân tích các chỉ số của vùng, lựa chọn vùng trọng điểm để sắp xếp kế hoạch ưu tiên đi kiểm tra", "› Đảm bảo trong năm các vùng đều được kiểm tra rà soát"],
            ["✔ Phân tích dữ liệu chi tiết để chọn ra các CH có nguy cơ cao cần kiểm tra trực tiếp", "✔ Ưu tiên phân bổ để tối đa các khu vực được kiểm tra (VD: 2CH/QLKV)"]
        ),
        (
            "⭐ Ưu điểm",
            ["› Có căn cứ để đánh giá QLKV, GĐV", "› Phương pháp phân tích chọn vùng không quá phức tạp", "› Triển khai kế hoạch đồng bộ, các khu vực hay CH không cảm thấy thiên vị"],
            ["✔ Tập trung chuyên sâu phát hiện nhanh được các sai phạm theo CH", "✔ Tối đa khả năng hiện diện với nhân sự tối ưu", "✔ Các CH và QLKV luôn trong trạng thái sẵn sàng được kiểm tra nên có thể tăng cường ý thức"]
        ),
        (
            "⛰️ Nhược điểm",
            ["› CH nắm bắt được quy luật kiểm tra có thể chủ quan", "› Dàn trải nhiều CH nhưng tính hiện diện thấp"],
            ["✔ Xây dựng kế hoạch sẽ khó khăn và cần nhân sự chuyên môn cao", "✔ Giảm hiện diện ở những CH không nghi vấn"]
        )
    ]
    
    for r_idx, row in enumerate(comp_data):
        for c_idx, data in enumerate(row):
            cell = tbl_comp.cell(r_idx + 1, c_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = c_light_gray if c_idx == 0 else c_white
            
            tf = cell.text_frame
            tf.word_wrap = True
            
            if c_idx == 0:
                p = tf.paragraphs[0]
                p.text = data
                apply_text_styling(p, font_size=10, bold=True, color=c_dark_gray, align=PP_ALIGN.CENTER)
            else:
                for idx, line in enumerate(data):
                    p = tf.paragraphs[0] if idx == 0 else tf.add_paragraph()
                    p.text = line
                    apply_text_styling(p, font_size=9, color=c_dark_gray)
                    p.space_before = Pt(3)

    # 4 Steps flowchart banner
    banner_y = Inches(5.6)
    banner_w = Inches(1.8)
    banner_gap = Inches(1.2)
    
    steps = ["📋 Hiện tại", "🔍 Phân tích", "🛡️ Xác minh", "👥 Thực thi"]
    
    for idx, s in enumerate(steps):
        s_pos = Inches(1.4) + idx * (banner_w + banner_gap)
        
        card = slide6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, s_pos, banner_y, banner_w, Inches(0.55))
        card.fill.solid()
        card.fill.fore_color.rgb = c_light_red if idx == 0 else c_light_blue
        card.line.color.rgb = c_red if idx == 0 else c_blue
        card.line.width = Pt(1.5)
        
        tf_s = card.text_frame
        p_s = tf_s.paragraphs[0]
        p_s.text = s
        apply_text_styling(p_s, font_size=9, bold=True, color=c_red if idx == 0 else c_blue, align=PP_ALIGN.CENTER)
        
        if idx < 3:
            # Draw Arrow Connector between cards
            arrow = slide6.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, s_pos + banner_w + Inches(0.2), banner_y + Inches(0.125), Inches(0.8), Inches(0.3))
            arrow.fill.solid()
            arrow.fill.fore_color.rgb = RGBColor(220, 220, 220)
            arrow.line.fill.background()

    # =========================================================================
    # SLIDE 8: Hành động (Roadmap & Actions)
    # =========================================================================
    print("Building Slide 8: Roadmap & Actions...")
    slide7 = prs.slides.add_slide(slide_layout)
    add_header_footer(slide7, "KẾ HOẠCH HÀNH ĐỘNG CỤ THỂ")
    
    # 3 Top cards
    top_w = Inches(3.9)
    top_gap = Inches(0.316)
    top_y = Inches(0.95)
    
    top_cards = [
        {"title": "🎯 Xây dựng kế hoạch kiểm kê phù hợp", "text": "Thường xuyên / liên tục phân tích số liệu để phân loại mức độ ưu tiên nhằm xây dựng kế hoạch tham gia TKK hợp lý/ kịp thời đảm bảo số liệu Tổng kiểm kê chính xác."},
        {"title": "📈 100% CH mới mở được TKK sau 1 - 2 tháng", "text": "khai trương nhằm đảm bảo tồn kho CH chính xác từ ban đầu và sớm phát hiện nguyên nhân thất thoát để kịp thời điều chỉnh tránh thất thoát lớn trong quá trình trước/ trong khai trương."},
        {"title": "🛡️ IT cải tiến kiểm kê hàng ngày tại CH", "text": "cải tiến phương án kiểm kê hàng ngày tại các CH thuộc nhóm có lịch sử thất thoát và rủi ro cao nhằm hiệu chỉnh phương án phù hợp mở rộng áp dụng đối với các năm tiếp theo."}
    ]
    
    for idx, card_data in enumerate(top_cards):
        x_pos = Inches(0.5) + idx * (top_w + top_gap)
        card = slide7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x_pos, top_y, top_w, Inches(1.3))
        card.fill.solid()
        card.fill.fore_color.rgb = c_white
        card.line.color.rgb = c_red
        card.line.width = Pt(1.5)
        
        tf_c = card.text_frame
        tf_c.word_wrap = True
        tf_c.margin_left = tf_c.margin_right = Inches(0.12)
        tf_c.margin_top = Inches(0.08)
        
        p_t = tf_c.paragraphs[0]
        p_t.text = card_data["title"]
        apply_text_styling(p_t, font_size=9, bold=True, color=c_red)
        
        p_b = tf_c.add_paragraph()
        p_b.text = card_data["text"]
        apply_text_styling(p_b, font_size=8, color=c_dark_gray)
        p_b.space_before = Pt(3)

    # Bottom Left Panel: Principles
    bl_w = Inches(5.6)
    bl_y = Inches(2.4)
    bl_h = Inches(4.5)
    
    bl_panel = slide7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.5), bl_y, bl_w, bl_h)
    bl_panel.fill.solid()
    bl_panel.fill.fore_color.rgb = c_light_gray
    bl_panel.line.color.rgb = RGBColor(200, 200, 200)
    
    # Title
    t_box = slide7.shapes.add_textbox(Inches(0.65), Inches(2.45), Inches(5.3), Inches(0.35))
    p_t = t_box.text_frame.paragraphs[0]
    p_t.text = "🔴 Nguyên tắc chọn CH tham gia TKK"
    apply_text_styling(p_t, font_size=11, bold=True, color=c_red)
    
    # 4 Colored Small Cards
    sc_w = Inches(1.2)
    sc_h = Inches(1.1)
    sc_gap = Inches(0.1)
    
    small_cards = [
        {"title": "🏪 DIO", "text": "DIO > 90 ngày 3 tháng liên tiếp.", "color": c_blue, "fill": c_light_blue},
        {"title": "🤝 Chuyển giao", "text": "Giá trị CG cao 3 tháng liên tiếp", "color": c_red, "fill": c_light_red},
        {"title": "📦 Hủy hàng", "text": "Giá trị hủy thấp 3 tháng liên tiếp.", "color": c_orange, "fill": c_light_orange},
        {"title": "🎟️ Coupon", "text": "Giá trị CP cao 3 tháng liên tiếp.", "color": c_purple, "fill": c_light_purple}
    ]
    
    for idx, sc in enumerate(small_cards):
        x_sc = Inches(0.65) + idx * (sc_w + sc_gap)
        sc_shape = slide7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x_sc, Inches(2.85), sc_w, sc_h)
        sc_shape.fill.solid()
        sc_shape.fill.fore_color.rgb = sc["fill"]
        sc_shape.line.color.rgb = sc["color"]
        
        tf_sc = sc_shape.text_frame
        tf_sc.word_wrap = True
        tf_sc.margin_left = tf_sc.margin_right = Inches(0.06)
        tf_sc.margin_top = Inches(0.06)
        
        p_sc1 = tf_sc.paragraphs[0]
        p_sc1.text = sc["title"]
        apply_text_styling(p_sc1, font_size=7.5, bold=True, color=sc["color"])
        
        p_sc2 = tf_sc.add_paragraph()
        p_sc2.text = sc["text"]
        apply_text_styling(p_sc2, font_size=6.2, color=c_dark_gray)
        p_sc2.space_before = Pt(2)
        
    # Bullets text block under the small cards
    b_box = slide7.shapes.add_textbox(Inches(0.65), Inches(4.05), Inches(5.3), Inches(2.7))
    tf_b = b_box.text_frame
    tf_b.word_wrap = True
    
    bullets = [
        "Nguyên tắc lấy chỉ số:",
        "• Chọn chỉ số nêu trên báo động (gian lận trục lợi);",
        "• Chuyển giao: (Q/Đ thể hiện HUB thường xuyên chuyển giao hàng hóa nguy cơ CG sai khi làm hệ thống); CH thực hiện CG do nhóm gian lận báo cáo để phi lợi nhuận và/hoặc nhằm tránh bị phát hiện tồn ảo cao;",
        "• Hủy hàng: Đổi hủy, sự cố xử lý đơn gây tồn ảo ảnh hưởng đến chỉ số, dịch vụ của cửa hàng. Trường hợp để xảy ra lâu dài sẽ dẫn đến mất kiểm soát hàng hóa tại CH;",
        "• Coupon cao: Nguy cơ tồn nhưng những sản phẩm tồn (hạn HSD) hết HSD chưa xử lý. Trường hợp để xảy ra lâu dài sẽ dẫn đến mất kiểm soát hàng hóa tại CH."
    ]
    
    for idx, line in enumerate(bullets):
        p = tf_b.paragraphs[0] if idx == 0 else tf_b.add_paragraph()
        p.text = line
        apply_text_styling(p, font_size=7, color=c_dark_gray)
        p.space_before = Pt(2)
        if idx == 0:
            p.font.bold = True
            
    # Bottom Right Panel: Matrix Table
    br_w = Inches(6.4)
    br_y = Inches(2.4)
    br_h = Inches(4.5)
    
    # Title
    t_box2 = slide7.shapes.add_textbox(Inches(6.6), Inches(2.45), Inches(6.0), Inches(0.35))
    p_t2 = t_box2.text_frame.paragraphs[0]
    p_t2.text = "🛡️ Phương án giám sát/ hậu kiểm KK gián tiếp"
    apply_text_styling(p_t2, font_size=11, bold=True, color=c_red)
    
    # Table layout
    table_shape = slide7.shapes.add_table(6, 4, Inches(6.6), Inches(2.85), br_w - Inches(0.2), Inches(3.9))
    tbl_act = table_shape.table
    
    tbl_act.columns[0].width = Inches(0.4)
    tbl_act.columns[1].width = Inches(1.3)
    tbl_act.columns[2].width = Inches(2.25)
    tbl_act.columns[3].width = Inches(2.25)
    
    tbl_headers = ["TT", "Nội dung", "Thực hiện", "Mục tiêu"]
    for c_idx, text in enumerate(tbl_headers):
        cell = tbl_act.cell(0, c_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = c_red
        p = cell.text_frame.paragraphs[0]
        p.text = text
        apply_text_styling(p, font_size=8, bold=True, color=c_white, align=PP_ALIGN.CENTER)
        
    table_act_data = [
        ("1", "📋 Xây dựng lịch\nkiểm kê", "Lên lịch kiểm kê chi tiết của từng CH theo từng tháng gửi CSVH thực hiện", "CSVH chủ động sắp xếp hàng hóa phục vụ công tác kiểm kê"),
        ("2", "🎯 Tạo PID kiểm kê", "Phân công khu vực phụ trách theo từng Vùng/ CV GSKK sẽ tạo PID kiểm kê các CH thuộc khu vực phụ trách trên hệ thống để CSVH thực hiện.", "Tránh trường hợp kiểm kê thiếu mã hàng hoặc có tình huống thất thoát, đảm bảo dữ liệu của mã hàng/CSKH khi trực tiếp kiểm kê."),
        ("3", "👥 Kiểm soát tại\ncửa hàng", "Phân ca CSNV làm việc để theo dõi kiểm kê tại cửa hàng", "Phát hiện các trường hợp gian lận tại quầy (QT/QĐ/HD Công ty), thực hiện cảnh báo, nhắc nhở ngay tại thời điểm kiểm kê để đề xuất xử lý vi phạm."),
        ("4", "🔍 Kiểm soát,\nrà soát số liệu", "Rà soát, phân tích, thẩm định số liệu trước và sau kiểm kê", "- Đưa ra cảnh báo, nhắc nhở CSVH xử lý triệt để các chứng từ chưa hoàn tất xử lý (nhập, xuất kho, hủy hàng...)\n- Phát hiện kịp thời các trường hợp có tồn xuất trả NCC, hủy phiếu nhập kho, điều chỉnh số liệu ảo trên hệ thống nhằm giảm giá trị CLKK;\n- Xác định được nguyên nhân dẫn đến thất thoát hàng hóa."),
        ("5", "📈 Kiểm kê trực tiếp\nđột xuất", "- Kiểm tra đột xuất trực tiếp tại CSVH ngay sau khi phát hiện các trường hợp nghi ngờ gian lận – cần chỉnh số liệu kiểm kê qua kiểm soát CMR và rà soát số liệu;\n- Phân tích số liệu hàng tháng, hàng quý theo từng GDV phụ trách để lên kế hoạch tham gia kiểm kê trực tiếp tại các CSVH có tỷ lệ CLKK/ hàng hủy bất thường so với tỷ lệ trung bình của Vùng (không thông báo trước).", "Phát hiện kịp thời các trường hợp tồn kho ảo, gian lận trực tiếp hàng hóa (nếu có)")
    ]
    
    for r_idx, row in enumerate(table_act_data):
        for c_idx, val in enumerate(row):
            cell = tbl_act.cell(r_idx + 1, c_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = c_light_gray if c_idx == 0 else c_white
            
            tf = cell.text_frame
            tf.word_wrap = True
            
            p = tf.paragraphs[0]
            p.text = val
            apply_text_styling(p, font_size=7, color=c_dark_gray)
            
            if c_idx == 0:
                p.font.bold = True
                p.font.color.rgb = c_blue
                p.alignment = PP_ALIGN.CENTER
            elif c_idx == 1:
                p.font.bold = True
                p.font.color.rgb = c_red
                
    # Save the native presentation
    output_path = "WinCommerce_Hoat_Dong_Trong_Tam_2026.pptx"
    prs.save(output_path)
    print(f"100% Native Vector PowerPoint successfully created at: {output_path}")

if __name__ == "__main__":
    create_presentation()
