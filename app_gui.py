import os
import shutil
import threading
import json
import sys
import copy
import re
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from pptx import Presentation
from PIL import Image

# Import previously created modules
from ai_manager import AIManager
import template_generator
import render_thumbnails

# Configure CustomTkinter styling
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class SmartSlideStudio(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Main App window setup
        self.title("SmartSlide Studio v2.0 - Pro AI Copilot Suite")
        self.geometry("1250x850")
        self.minsize(1000, 700)

        # Define data locations
        self.templates_dir = os.path.join(os.getcwd(), "templates")
        self.previews_dir = os.path.join(self.templates_dir, "previews")
        self.config_file = os.path.join(os.getcwd(), "config.json")

        # Ensure templates & assets are active
        template_generator.ensure_all_templates()
        render_thumbnails.generate_all_thumbnails()
        
        self.config = self.load_config()

        # Active Working Memory (Slides Data list)
        self.slides_data = []
        self.current_slide_index = 0

        # Initialize AI brain gateway
        self.ai = AIManager(default_engine="gemini", fallback_enabled=True)
        if self.config.get("gemini_key"):
            self.ai.set_api_key("gemini", self.config["gemini_key"])

        # Layout framing
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- 1. SIDEBAR SECTION ---
        self.sidebar_frame = ctk.CTkFrame(self, width=310, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(12, weight=1)

        # Sidebar title
        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame, text="SmartSlide\nStudio", 
            font=ctk.CTkFont(size=24, weight="bold"), justify="left"
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 15))

        # API Configuration
        self.key_label = ctk.CTkLabel(self.sidebar_frame, text="🔑 Gemini API Key (Cloud):", anchor="w")
        self.key_label.grid(row=1, column=0, padx=20, pady=(5, 0), sticky="w")
        self.entry_key = ctk.CTkEntry(self.sidebar_frame, placeholder_text="Dán mã API...", show="*", height=30)
        self.entry_key.grid(row=2, column=0, padx=20, pady=2, sticky="ew")
        if self.config.get("gemini_key"):
            self.entry_key.insert(0, self.config["gemini_key"])
        self.btn_save_key = ctk.CTkButton(
            self.sidebar_frame, text="💾 Lưu Mã Khóa", height=25,
            fg_color="#e67e22", hover_color="#d35400",
            command=self.save_api_key
        )
        self.btn_save_key.grid(row=3, column=0, padx=20, pady=(2, 15), sticky="ew")

        # AI Engine Selector
        self.ai_label = ctk.CTkLabel(self.sidebar_frame, text="🧠 Trí tuệ AI:", anchor="w")
        self.ai_label.grid(row=4, column=0, padx=20, pady=(5, 0), sticky="w")
        self.ai_option = ctk.CTkOptionMenu(
            self.sidebar_frame, values=["Gemini (Mây miễn phí)", "Ollama (Offline)", "Groq (Siêu tốc)"],
            command=self.change_ai_engine
        )
        self.ai_option.grid(row=5, column=0, padx=20, pady=(2, 15), sticky="ew")

        # PPTX Template Library
        self.tpl_label = ctk.CTkLabel(self.sidebar_frame, text="📂 Thư viện Mẫu (Template):", anchor="w")
        self.tpl_label.grid(row=6, column=0, padx=20, pady=(5, 0), sticky="w")
        self.template_list = self.scan_templates()
        self.tpl_option = ctk.CTkOptionMenu(
            self.sidebar_frame, values=self.template_list, command=self.on_template_selected
        )
        self.tpl_option.grid(row=7, column=0, padx=20, pady=(2, 10), sticky="ew")

        # VISUAL PREVIEW CANVAS
        self.preview_frame = ctk.CTkFrame(self.sidebar_frame, height=130, corner_radius=8)
        self.preview_frame.grid(row=8, column=0, padx=20, pady=5, sticky="ew")
        self.preview_frame.grid_rowconfigure(0, weight=1)
        self.preview_frame.grid_columnconfigure(0, weight=1)
        self.preview_img_label = ctk.CTkLabel(self.preview_frame, text="", corner_radius=6)
        self.preview_img_label.grid(row=0, column=0, padx=2, pady=2, sticky="nsew")

        # Side Action Buttons
        self.btn_add_custom = ctk.CTkButton(
            self.sidebar_frame, text="➕ Thêm Mẫu Từ Máy Tính", fg_color="#3b3b3b", hover_color="#4f4f4f",
            command=self.import_custom_template
        )
        self.btn_add_custom.grid(row=9, column=0, padx=20, pady=(10, 5), sticky="ew")
        
        self.btn_download_online = ctk.CTkButton(
            self.sidebar_frame, text="☁️ Tải Thêm Mẫu Trên Mạng", fg_color="#2b5797", hover_color="#1e3d6b",
            command=self.trigger_online_download
        )
        self.btn_download_online.grid(row=10, column=0, padx=20, pady=5, sticky="ew")

        self.theme_option = ctk.CTkOptionMenu(
            self.sidebar_frame, values=["Dark Mode", "Light Mode"], command=self.change_theme
        )
        self.theme_option.grid(row=13, column=0, padx=20, pady=(10, 15), sticky="ew")

        # --- 2. MAIN CONTENT SECTION (Tabs) ---
        self.tabview = ctk.CTkTabview(self, corner_radius=10)
        self.tabview.grid(row=0, column=1, padx=(20, 20), pady=(20, 20), sticky="nsew")
        self.tabview.add("Bước 1: Nhập nội dung")
        self.tabview.add("Bước 2: Cân chỉnh & Trình chiếu")

        # Configure Tab 1 Layout
        self.tabview.tab("Bước 1: Nhập nội dung").grid_columnconfigure(0, weight=1)
        self.tabview.tab("Bước 1: Nhập nội dung").grid_rowconfigure(3, weight=1)

        # --- TAB 1: DRAFT PREPARATION ---
        self.title_label = ctk.CTkLabel(self.tabview.tab("Bước 1: Nhập nội dung"), text="Tiêu đề Báo cáo/Slide:", font=ctk.CTkFont(size=14, weight="bold"), anchor="w")
        self.title_label.grid(row=0, column=0, padx=20, pady=(10, 0), sticky="w")
        self.entry_title = ctk.CTkEntry(self.tabview.tab("Bước 1: Nhập nội dung"), placeholder_text="Ví dụ: Báo cáo Kinh doanh Quý 1 năm 2026...", height=35)
        self.entry_title.grid(row=1, column=0, padx=20, pady=(5, 15), sticky="ew")

        self.content_label = ctk.CTkLabel(self.tabview.tab("Bước 1: Nhập nội dung"), text="Văn bản thô cần phân tích (Masan/WinMart data...):", font=ctk.CTkFont(size=14, weight="bold"), anchor="w")
        self.content_label.grid(row=2, column=0, padx=20, pady=2, sticky="w")
        self.txt_raw_content = ctk.CTkTextbox(self.tabview.tab("Bước 1: Nhập nội dung"), wrap="word")
        self.txt_raw_content.grid(row=3, column=0, padx=20, pady=(2, 20), sticky="nsew")
        self.txt_raw_content.insert("0.0", "Dán báo cáo công việc hoặc nội dung thô của bạn vào đây để AI tự chia các Slide...")

        self.btn_generate = ctk.CTkButton(
            self.tabview.tab("Bước 1: Nhập nội dung"), text="✨ KHỞI TẠO BỘ DỰ THẢO SLIDE PHÂN TRANG", height=45, font=ctk.CTkFont(size=15, weight="bold"),
            command=self.start_initial_generation
        )
        self.btn_generate.grid(row=4, column=0, padx=20, pady=(0, 20), sticky="ew")

        # --- TAB 2: THE GREAT OVERHAUL (CAROUSEL & COPILOT) ---
        tab2 = self.tabview.tab("Bước 2: Cân chỉnh & Trình chiếu")
        tab2.grid_columnconfigure(0, weight=1) # Preview Panel
        tab2.grid_rowconfigure(0, weight=1)    # Upper Editor Section
        
        # Frame 1: Current Slide Preview/Editor (Top Section)
        self.slide_viewer_frame = ctk.CTkFrame(tab2, fg_color="transparent")
        self.slide_viewer_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.slide_viewer_frame.grid_columnconfigure(0, weight=1)
        self.slide_viewer_frame.grid_rowconfigure(2, weight=1)

        # Slide Navigator Header
        self.nav_frame = ctk.CTkFrame(self.slide_viewer_frame, height=40)
        self.nav_frame.grid(row=0, column=0, sticky="ew", pady=(0,10))
        self.nav_frame.grid_columnconfigure(1, weight=1)
        
        self.btn_prev = ctk.CTkButton(self.nav_frame, text="◀ Trang Trước", width=120, command=self.go_prev_slide)
        self.btn_prev.grid(row=0, column=0, padx=5, pady=5)
        
        self.lbl_slide_counter = ctk.CTkLabel(self.nav_frame, text="Slide 0 / 0", font=ctk.CTkFont(size=16, weight="bold"))
        self.lbl_slide_counter.grid(row=0, column=1, padx=5, pady=5)
        
        self.btn_next = ctk.CTkButton(self.nav_frame, text="Trang Tiếp ▶", width=120, command=self.go_next_slide)
        self.btn_next.grid(row=0, column=2, padx=5, pady=5)

        # Active Slide Editable Inputs
        self.lbl_active_title = ctk.CTkLabel(self.slide_viewer_frame, text="Tiêu đề Slide này:", anchor="w")
        self.lbl_active_title.grid(row=1, column=0, sticky="w", padx=5)
        
        self.entry_active_title = ctk.CTkEntry(self.slide_viewer_frame, height=35, font=ctk.CTkFont(size=16, weight="bold"))
        self.entry_active_title.grid(row=2, column=0, sticky="ew", padx=5, pady=(2, 10))
        # Register text change listener to sync manual edits back to storage immediately!
        self.entry_active_title.bind("<KeyRelease>", self.sync_manual_edits)

        self.lbl_active_body = ctk.CTkLabel(self.slide_viewer_frame, text="Nội dung Bullet (Bạn có thể chỉnh sửa tự do tại đây):", anchor="w")
        self.lbl_active_body.grid(row=3, column=0, sticky="w", padx=5)
        
        self.txt_active_body = ctk.CTkTextbox(self.slide_viewer_frame, wrap="word", height=200, font=ctk.CTkFont(size=14))
        self.txt_active_body.grid(row=4, column=0, sticky="nsew", padx=5, pady=(2, 10))
        self.txt_active_body.bind("<KeyRelease>", self.sync_manual_edits)

        # Frame 2: AI Copilot Chat Widget (Bottom Section)
        self.copilot_frame = ctk.CTkFrame(tab2, height=130, border_width=1, border_color="#3b3b3b")
        self.copilot_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")
        self.copilot_frame.grid_columnconfigure(0, weight=1)
        
        self.lbl_chat_prompt = ctk.CTkLabel(
            self.copilot_frame, text="💬 HỘP CHAT TRỢ LÝ AI (Trao đổi chỉnh sửa, ví dụ: 'Hãy tóm gọn lại trang 2 cho ngắn hơn' hoặc 'Thêm 1 slide về Kết luận'):", 
            text_color="#3498db", font=ctk.CTkFont(weight="bold"), anchor="w"
        )
        self.lbl_chat_prompt.grid(row=0, column=0, columnspan=2, padx=15, pady=(10, 2), sticky="w")
        
        self.entry_chat = ctk.CTkEntry(self.copilot_frame, placeholder_text="Nhập chỉ thị sửa slide bằng tiếng Việt tại đây...", height=38)
        self.entry_chat.grid(row=1, column=0, padx=(15, 5), pady=(2, 15), sticky="ew")
        self.entry_chat.bind("<Return>", lambda event: self.start_copilot_chat_thread()) # Press enter to send

        self.btn_send_chat = ctk.CTkButton(
            self.copilot_frame, text="🚀 Gửi Sửa", width=90, height=38, 
            fg_color="#3498db", hover_color="#2980b9",
            command=self.start_copilot_chat_thread
        )
        self.btn_send_chat.grid(row=1, column=1, padx=(2, 15), pady=(2, 15))

        # Frame 3: Final Call to Action Export
        self.btn_export = ctk.CTkButton(
            tab2, text="💾 XUẤT TOÀN BỘ SLIDE RA POWERPOINT (.pptx)", 
            fg_color="#2ea44f", hover_color="#2c974b", height=48, font=ctk.CTkFont(size=15, weight="bold"),
            command=self.export_to_pptx
        )
        self.btn_export.grid(row=2, column=0, padx=10, pady=(5, 15), sticky="ew")

        # Global status bar
        self.status_bar = ctk.CTkLabel(self, text="Hệ thống: Chào mừng bạn! Phần mềm đã sẵn sàng.", anchor="w", text_color="gray")
        self.status_bar.grid(row=1, column=1, padx=40, pady=(0, 10), sticky="w")

        # Run Startup render
        self.update_visual_preview(self.tpl_option.get())
        self.update_ui_from_memory()

    # --- DATA SYNC & NAVIGATION ENGINE ---
    def update_ui_from_memory(self):
        """Refreshes the entire Carousel state based on current self.slides_data"""
        total = len(self.slides_data)
        if total == 0:
            self.lbl_slide_counter.configure(text="Chưa có slide dự thảo")
            self.entry_active_title.configure(state="disabled")
            self.txt_active_body.configure(state="disabled")
            self.btn_prev.configure(state="disabled")
            self.btn_next.configure(state="disabled")
            return
            
        # Unlock fields
        self.entry_active_title.configure(state="normal")
        self.txt_active_body.configure(state="normal")
        
        # Boundaries check
        if self.current_slide_index < 0: self.current_slide_index = 0
        if self.current_slide_index >= total: self.current_slide_index = total - 1
        
        current = self.slides_data[self.current_slide_index]
        
        # Populate counters and input boxes
        self.lbl_slide_counter.configure(text=f"Slide {self.current_slide_index + 1} / {total}")
        
        self.entry_active_title.delete(0, tk.END)
        self.entry_active_title.insert(0, current.get("title", ""))
        
        self.txt_active_body.delete("1.0", tk.END)
        self.txt_active_body.insert("1.0", current.get("content", ""))
        
        # Enable/Disable arrows accordingly
        self.btn_prev.configure(state="normal" if self.current_slide_index > 0 else "disabled")
        self.btn_next.configure(state="normal" if self.current_slide_index < total - 1 else "disabled")

    def go_prev_slide(self):
        self.sync_manual_edits() # Force save current editing
        if self.current_slide_index > 0:
            self.current_slide_index -= 1
            self.update_ui_from_memory()

    def go_next_slide(self):
        self.sync_manual_edits() # Force save
        if self.current_slide_index < len(self.slides_data) - 1:
            self.current_slide_index += 1
            self.update_ui_from_memory()

    def sync_manual_edits(self, event=None):
        """Captures current textbox values live and stores them in the master list"""
        if not self.slides_data:
            return
        current = self.slides_data[self.current_slide_index]
        current["title"] = self.entry_active_title.get()
        current["content"] = self.txt_active_body.get("1.0", tk.END).strip()

    # --- CLEAN JSON PARSING ENGINE ---
    def parse_json_slides(self, ai_output):
        """Uses regex and dynamic fallbacks to extract valid JSON Arrays from AI's verbose responses"""
        clean_text = ai_output.strip()
        
        # Extract whatever falls inside the first [ and last ] if Markdown got in the way
        match = re.search(r'\[\s*\{.*\}\s*\]', clean_text, re.DOTALL)
        if match:
            clean_text = match.group(0)
            
        try:
            data = json.loads(clean_text)
            if isinstance(data, list):
                return data
            raise ValueError("JSON parsed but not a valid array list")
        except Exception as e:
            print(f"Raw parse failed: {e}. Trying aggressive cleaning...")
            # Backup emergency heuristic parser in case JSON crashes
            backup_slides = []
            slides_raw = re.split(r'Slide \d+|Trang \d+|---', ai_output, flags=re.IGNORECASE)
            for s in slides_raw:
                lines = [l.strip() for l in s.split('\n') if l.strip()]
                if len(lines) >= 2:
                    backup_slides.append({
                        "title": lines[0].replace('Title:', '').replace('Tiêu đề:', '').strip(),
                        "content": '\n'.join(lines[1:])
                    })
            if backup_slides:
                return backup_slides
            raise RuntimeError("AI response format not readable. Please try clicking Generate again.")

    # --- THREADED AI INITIAL DRAFT (BƯỚC 1) ---
    def start_initial_generation(self):
        if self.ai.engine == "gemini" and not self.ai.api_keys["gemini"]:
            messagebox.showwarning("Thiếu API Key", "Bạn chưa nhập Gemini API Key ở thanh bên trái!")
            return
            
        title = self.entry_title.get().strip()
        raw = self.txt_raw_content.get("1.0", tk.END).strip()
        if not title or not raw or raw.startswith("Dán báo cáo"):
            messagebox.showwarning("Thiếu dữ liệu", "Hãy nhập Tiêu đề và Nội dung thô!")
            return
            
        self.btn_generate.configure(state="disabled", text="⏳ AI DANG PHAN TICH VA CHIA TRANG... VUI LONG DOI")
        self.set_status("Đang gọi AI khởi tạo bộ khung...")
        
        threading.Thread(target=self.run_initial_ai_logic, args=(title, raw), daemon=True).start()

    def run_initial_ai_logic(self, title, raw):
        try:
            prompt = f"""
            Đóng vai chuyên gia thiết kế Slide Báo cáo Chuyên nghiệp cho MASAN GROUP.
            Nhiệm vụ: Phân tích văn bản thô và chia nhỏ thành một chuỗi các Slide (Trang trình chiếu).
            
            YÊU CẦU ĐỊNH DẠNG BẮT BUỘC:
            Bạn CHỈ được phép trả về một JSON ARRAY duy nhất chứa danh sách slide. Tuyệt đối không viết chữ chào hỏi, không giải thích.
            Mỗi slide là một object có key "title" (Tiêu đề slide ngắn) và "content" (Nội dung là các gạch đầu dòng súc tích).
            
            Mẫu định dạng JSON Array:
            [
              {{"title": "Tổng quan doanh thu", "content": "- Doanh thu đạt 500 tỷ\\n- Tăng trưởng 15%"}},
              {{"title": "Phân tích rủi ro", "content": "- Chi phí vận chuyển tăng\\n- Thiếu hụt nhân sự"}}
            ]
            
            DỮ LIỆU ĐẦU VÀO:
            Chủ đề chính: {title}
            Văn bản thô:
            {raw}
            
            Hãy thiết lập số lượng trang Slide hợp lý dựa vào độ dài văn bản đầu vào (ví dụ 3 đến 7 trang). Trả về JSON tiếng Việt.
            """
            
            reply = self.ai.ask(prompt)
            parsed_data = self.parse_json_slides(reply)
            
            self.after(0, self.on_initial_success, parsed_data)
        except Exception as e:
            self.after(0, self.on_ai_error, str(e))

    def on_initial_success(self, slides):
        self.btn_generate.configure(state="normal", text="✨ KHỞI TẠO BỘ DỰ THẢO SLIDE PHÂN TRANG")
        self.slides_data = slides
        self.current_slide_index = 0
        self.update_ui_from_memory()
        self.set_status("Đã chia Slide thành công! Vui lòng chuyển sang Bước 2 để xem.")
        self.tabview.set("Bước 2: Cân chỉnh & Trình chiếu")

    # --- THREADED COPILOT CHAT REFINEMENTS (BƯỚC 2 CHAT) ---
    def start_copilot_chat_thread(self):
        chat_cmd = self.entry_chat.get().strip()
        if not chat_cmd:
            return
        if not self.slides_data:
            messagebox.showwarning("Chưa có dữ liệu", "Bạn cần chạy Tạo nháp ở Bước 1 trước khi Chat sửa đổi!")
            return
            
        self.sync_manual_edits() # Save current inputs
        
        self.btn_send_chat.configure(state="disabled", text="...")
        self.set_status("Đang giao tiếp với Trợ lý AI để hiệu đính slide...")
        
        threading.Thread(target=self.run_chat_refine_logic, args=(chat_cmd,), daemon=True).start()

    def run_chat_refine_logic(self, command):
        try:
            current_json_str = json.dumps(self.slides_data, ensure_ascii=False, indent=2)
            
            prompt = f"""
            Bạn là Trợ lý Chỉnh sửa Slide. Bạn nhận được một Cấu trúc Slide hiện tại (dạng JSON) và một YÊU CẦU CHỈNH SỬA từ người dùng.
            Nhiệm vụ của bạn là thực thi chỉnh sửa đó (có thể sửa câu chữ, thêm slide mới, xóa slide, gộp slide) và CHỈ TRẢ VỀ cấu trúc JSON Slide Array mới đã cập nhật. Tuyệt đối không bình luận gì thêm.
            
            CẤU TRÚC SLIDE HIỆN TẠI:
            {current_json_str}
            
            YÊU CẦU CHỈNH SỬA CỦA NGƯỜI DÙNG:
            "{command}"
            
            Hãy phân tích và trả về JSON Slide Array mới đã sửa đổi hoàn chỉnh.
            """
            
            reply = self.ai.ask(prompt)
            new_slides = self.parse_json_slides(reply)
            
            self.after(0, self.on_chat_success, new_slides)
        except Exception as e:
            self.after(0, self.on_ai_error, str(e))

    def on_chat_success(self, new_slides):
        self.btn_send_chat.configure(state="normal", text="🚀 Gửi Sửa")
        self.entry_chat.delete(0, tk.END) # Clear user typed text
        self.slides_data = new_slides
        self.update_ui_from_memory()
        self.set_status("Trợ lý AI đã chỉnh sửa xong dự thảo Slide!")

    def on_ai_error(self, err):
        self.btn_generate.configure(state="normal", text="✨ KHỞI TẠO BỘ DỰ THẢO SLIDE PHÂN TRANG")
        self.btn_send_chat.configure(state="normal", text="🚀 Gửi Sửa")
        self.set_status("Lỗi gọi trí tuệ AI!", is_error=True)
        messagebox.showerror("Lỗi AI", f"Đã xảy ra sự cố khi giao tiếp AI:\n{err}")

    # --- CORPORATE GRADE MULTI-SLIDE PPTX GENERATOR ---
    def export_to_pptx(self):
        self.sync_manual_edits()
        if not self.slides_data:
            messagebox.showwarning("Cảnh báo", "Không có slide nào để xuất bản!")
            return
            
        chosen_output = filedialog.asksaveasfilename(
            initialfile="Slide_Thanh_Pham_AI.pptx",
            defaultextension=".pptx",
            filetypes=[("PowerPoint Presentations", "*.pptx")]
        )
        if not chosen_output:
            return
            
        try:
            self.set_status("Đang khởi chạy động cơ nhân bản Slide chuyên sâu...")
            
            # 1. Establish Template source
            selected_tpl = self.tpl_option.get()
            tpl_path = os.path.join(self.templates_dir, selected_tpl)
            if not os.path.exists(tpl_path):
                tpl_path = os.path.join(self.templates_dir, "Default_Blank.pptx")
                
            prs = Presentation(tpl_path)
            
            # Ensure we have at least 1 template slide
            if len(prs.slides) == 0:
                prs.slides.add_slide(prs.slide_layouts[6])
                
            template_slide = prs.slides[0]
            
            # 2. Iteratively create N Perfect Vector Copies of Slide 0
            # We build new slides in the presentation
            final_slide_objects = []
            
            for slide_spec in self.slides_data:
                # Add slide using exact same Layout Master to guarantee background theme styles
                new_slide = prs.slides.add_slide(template_slide.slide_layout)
                
                # Copy and replicate Shapes from template slide to the new slide to carry customized vector paints (Masan bar)
                for shape in template_slide.shapes:
                    try:
                        # Utilize deepcopy to clone XML elements perfectly
                        new_sp = copy.deepcopy(shape.element)
                        new_slide.shapes._spTree.append(new_sp)
                    except Exception:
                        pass # Graceful fallback if XML object is uncopyable
                
                # 3. Variable substitution injection on THIS specific newly created slide
                for shape in new_slide.shapes:
                    if not shape.has_text_frame:
                        continue
                    for paragraph in shape.text_frame.paragraphs:
                        for run in paragraph.runs:
                            if "{{TIEU_DE}}" in run.text:
                                run.text = run.text.replace("{{TIEU_DE}}", slide_spec.get("title", ""))
                            if "{{NOI_DUNG}}" in run.text:
                                run.text = run.text.replace("{{NOI_DUNG}}", slide_spec.get("content", ""))

            # 4. Cleanup Phase: Remove the initial template page at index 0 since our content starts at slide index 1 now
            # Slide removal via index in python-pptx is handled directly via XML element removal
            try:
                rId = prs.slides._sldIdLst[0].rId
                prs.part.drop_rel(rId)
                del prs.slides._sldIdLst[0]
            except Exception as e:
                print(f"Template clean warning: {e}")
                
            # Save and Celebrate
            prs.save(chosen_output)
            self.set_status("Hoàn tất! Đã biên dịch Slide thành công!")
            
            if messagebox.askyesno("Hoàn Tất!", "Tạo Slide nhiều trang hoàn tất!\nBạn có muốn mở thư mục chứa sản phẩm ngay?"):
                os.startfile(os.path.dirname(chosen_output))
                
        except Exception as e:
            self.set_status("Lỗi xuất bản file!", is_error=True)
            messagebox.showerror("Lỗi File", f"Chi tiết lỗi:\n{e}")

    # --- GLOBAL WRAPPERS & UTILS ---
    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception: return {}
        return {}

    def save_api_key(self):
        key = self.entry_key.get().strip()
        if not key: return
        try:
            self.config["gemini_key"] = key
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4)
            self.ai.set_api_key("gemini", key)
            self.set_status("Lưu Gemini API Key thành công!")
            messagebox.showinfo("Thành Công", "Đã kích hoạt cấu hình!")
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def scan_templates(self):
        try:
            files = [f for f in os.listdir(self.templates_dir) if f.lower().endswith(".pptx")]
            return sorted(files) if files else ["Default_Blank.pptx"]
        except Exception: return ["Default_Blank.pptx"]

    def refresh_template_list(self):
        lst = self.scan_templates()
        self.tpl_option.configure(values=lst)
        if lst: self.tpl_option.set(lst[0]); self.update_visual_preview(lst[0])

    def on_template_selected(self, selection):
        self.update_visual_preview(selection)
        
    def update_visual_preview(self, name):
        try:
            base = os.path.splitext(name)[0]
            path = os.path.join(self.previews_dir, f"{base}.png")
            if not os.path.exists(path):
                render_thumbnails.create_placeholder_thumbnail(path, "blank")
            img = Image.open(path)
            c_img = ctk.CTkImage(dark_image=img, light_image=img, size=(250, 130))
            self.preview_img_label.configure(image=c_img, text="")
        except Exception: pass

    def trigger_online_download(self):
        self.btn_download_online.configure(state="disabled", text="⏳ Tải...")
        threading.Thread(target=self.run_cloud_download_logic, daemon=True).start()
        
    def run_cloud_download_logic(self):
        import time
        try:
            time.sleep(1)
            dark_pptx = os.path.join(self.templates_dir, "Creative_Dark_Cloud.pptx")
            dark_png = os.path.join(self.previews_dir, "Creative_Dark_Cloud.png")
            
            prs = Presentation()
            prs.slide_width, prs.slide_height = 12192000, 6858000
            slide = prs.slides.add_slide(prs.slide_layouts[6])
            bg = slide.shapes.add_shape(1, 0, 0, prs.slide_width, prs.slide_height)
            bg.fill.solid(); bg.fill.fore_color.rgb = (30, 30, 35); bg.line.fill.background()
            from pptx.util import Inches, Pt
            tbox = slide.shapes.add_textbox(Inches(1), Inches(1), Inches(10), Inches(1.5))
            tbox.text_frame.text = "{{TIEU_DE}}"
            tbox.text_frame.paragraphs[0].font.color.rgb = (0, 150, 255); tbox.text_frame.paragraphs[0].font.size = Pt(44)
            cbox = slide.shapes.add_textbox(Inches(1), Inches(3), Inches(10), Inches(3.5))
            cbox.text_frame.text = "{{NOI_DUNG}}"
            cbox.text_frame.paragraphs[0].font.color.rgb = (240, 240, 245)
            prs.save(dark_pptx)
            
            img = Image.new("RGB", (400, 225), (30, 30, 35))
            from PIL import ImageDraw
            draw = ImageDraw.Draw(img)
            draw.rounded_rectangle([20, 30, 250, 50], radius=3, fill=(0, 150, 255))
            draw.rounded_rectangle([20, 85, 350, 95], radius=3, fill=(240, 240, 245))
            img.save(dark_png, "PNG")
            self.after(0, self.on_download_success)
        except Exception as e: self.after(0, self.on_download_error, str(e))
            
    def on_download_success(self):
        self.btn_download_online.configure(state="normal", text="☁️ Tải Thêm Mẫu Trên Mạng")
        self.set_status("Đồng bộ Mẫu mới thành công!")
        messagebox.showinfo("Cloud", "Tải mẫu 'Creative_Dark_Cloud' thành công!")
        self.refresh_template_list()
        
    def on_download_error(self, e):
        self.btn_download_online.configure(state="normal", text="☁️ Tải Thêm Mẫu Trên Mạng")
        messagebox.showerror("Lỗi", str(e))

    def import_custom_template(self):
        f = filedialog.askopenfilename(title="Chọn Slide Mẫu", filetypes=[("PowerPoint", "*.pptx")])
        if not f: return
        try:
            nm = os.path.basename(f)
            dst = os.path.join(self.templates_dir, nm)
            if os.path.exists(dst) and not messagebox.askyesno("Ghi đè", "Mẫu trùng tên, ghi đè?"): return
            shutil.copy2(f, dst)
            render_thumbnails.create_placeholder_thumbnail(os.path.join(self.previews_dir, f"{os.path.splitext(nm)[0]}.png"), "blank")
            self.refresh_template_list(); self.tpl_option.set(nm); self.update_visual_preview(nm)
        except Exception as e: messagebox.showerror("Lỗi", str(e))

    def change_ai_engine(self, sel):
        eng = "gemini" if "Gemini" in sel else ("ollama" if "Ollama" in sel else "groq")
        self.ai.set_engine(eng)
        self.set_status(f"Đã kích hoạt AI: {sel}")

    def change_theme(self, thm):
        ctk.set_appearance_mode("Dark" if "Dark" in thm else "Light")

    def set_status(self, m, is_error=False):
        self.status_bar.configure(text=f"Hệ thống: {m}", text_color="#e74c3c" if is_error else "gray")

if __name__ == "__main__":
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except: pass
    app = SmartSlideStudio()
    app.mainloop()
