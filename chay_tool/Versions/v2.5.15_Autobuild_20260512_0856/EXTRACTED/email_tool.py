# -*- coding: utf-8 -*-
"""
Email Data Extractor - TĐMB Tool (Hybrid Architecture v2.0)
Kiến trúc: Regex Fast Track → Gemini AI Rescue → Validation & Sink
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, simpledialog, filedialog
import json
import threading
import os
import re
import glob
import openpyxl
from datetime import datetime
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side

# Import core logic
from core_logic import (
    FOLDER, EXCEL_NAME, SHEET_NAME, DATA_START_ROW, REQUIRED_FIELDS,
    GEMINI_AVAILABLE, process_msg_file, init_gemini
)

# Thư mục con chứa file email xử lý
EMAIL_FOLDER = os.path.join(FOLDER, "emails")
if not os.path.exists(EMAIL_FOLDER):
    try: os.makedirs(EMAIL_FOLDER)
    except: pass



# ─── COLORS ───────────────────────────────────────────────────────────────────
BG_DARK   = "#0f1117"
BG_CARD   = "#1a1d2e"
BG_PANEL  = "#13151f"
ACCENT    = "#6c63ff"
ACCENT2   = "#a78bfa"
SUCCESS   = "#22c55e"
ERROR_COL = "#ef4444"
WARNING   = "#f59e0b"
TEXT_PRI  = "#f1f5f9"
TEXT_SEC  = "#94a3b8"
BORDER_C  = "#2d3148"
HIGHLIGHT_YELLOW = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")


# ─── EXCEL WRITER ─────────────────────────────────────────────────────────────

def write_to_excel(results, excel_path, log_callback=None):
    wb = openpyxl.load_workbook(excel_path)
    ws = wb[SHEET_NAME]

    # Find next empty row
    next_row = DATA_START_ROW
    for i in range(DATA_START_ROW, ws.max_row + 2):
        val = ws.cell(row=i, column=5).value
        if val is None or str(val).strip() == "":
            next_row = i; break
    else:
        next_row = ws.max_row + 1

    stt_start = max(1, next_row - DATA_START_ROW + 1)

    # ── DEDUPLICATION ──
    earliest, latest = {}, {}
    for res in results:
        if not res["success"]: continue
        data = res.get("data", {})
        ma_mb = data.get("ma_mb", "").strip().upper()
        if not ma_mb:
            key = res.get("file", "unknown")
            earliest[key] = res; latest[key] = res; continue

        ngay_tra = data.get("ngay_tra")
        if ma_mb not in earliest: earliest[ma_mb] = res
        else:
            ex_date = earliest[ma_mb]["data"].get("ngay_tra")
            if ngay_tra and (ex_date is None or (isinstance(ngay_tra, datetime) and isinstance(ex_date, datetime) and ngay_tra < ex_date)):
                earliest[ma_mb] = res

        if ma_mb not in latest: latest[ma_mb] = res
        else:
            la_date = latest[ma_mb]["data"].get("ngay_tra")
            if ngay_tra and (la_date is None or (isinstance(ngay_tra, datetime) and isinstance(la_date, datetime) and ngay_tra > la_date)):
                latest[ma_mb] = res

    results_to_write = []
    for key, early_res in earliest.items():
        merged = dict(early_res)
        merged["data"] = dict(early_res["data"])
        if key in latest:
            late_data = latest[key]["data"]
            merged["data"]["chi_tiet_thamdinh"] = late_data.get("chi_tiet_thamdinh", "")
            merged["data"]["gia_thue_sum"] = late_data.get("gia_thue_sum", "")
            merged["data"]["hspl"] = late_data.get("hspl", "")
            merged["data"]["ghi_chu"] = late_data.get("ghi_chu", "")
            merged["data"]["ngay_tra"] = late_data.get("ngay_tra")
        results_to_write.append(merged)

    # ── WRITE ROWS ──
    COL_MAP = [
        (1, None),  # STT - computed
        (2, "thang"), (3, "ngay_nhan"), (4, "ngay_tra"),
        (5, "ma_mb"), (6, "tinh_trang"), (7, "thong_tin_mb"),
        (8, "tinh"), (9, "dtt"), (10, "gia_thue_vat"),
        (11, "bct"), (12, "cv_tkmb"),
        (13, "chi_tiet_thamdinh"), (14, "gia_thue_sum"),
        (15, "hspl"), (16, "ghi_chu"),
    ]

    written = 0
    for i, r in enumerate(results_to_write):
        if not r["success"]: continue
        d = r["data"]
        row_num = next_row + written
        stt = stt_start + written
        missing = r.get("missing_fields", [])

        # Convert price string to number
        gia = d.get("gia_thue_vat", "")
        try: gia_num = float(str(gia).replace(".", "").replace(",", "").strip())
        except: gia_num = gia

        dtt_raw = d.get("dtt", "")
        try: dtt_num = float(str(dtt_raw).replace(",", ".").strip())
        except: dtt_num = dtt_raw

        ws.cell(row=row_num, column=1, value=stt)
        ws.cell(row=row_num, column=2, value=d.get("thang"))
        ws.cell(row=row_num, column=3, value=d.get("ngay_nhan"))
        ws.cell(row=row_num, column=4, value=d.get("ngay_tra"))
        ws.cell(row=row_num, column=5, value=d.get("ma_mb", ""))
        ws.cell(row=row_num, column=6, value=d.get("tinh_trang", ""))
        ws.cell(row=row_num, column=7, value=d.get("thong_tin_mb", ""))
        ws.cell(row=row_num, column=8, value=d.get("tinh", ""))
        ws.cell(row=row_num, column=9, value=dtt_num)
        ws.cell(row=row_num, column=10, value=gia_num)
        ws.cell(row=row_num, column=11, value=d.get("bct", ""))
        ws.cell(row=row_num, column=12, value=d.get("cv_tkmb", ""))
        ws.cell(row=row_num, column=13, value=d.get("chi_tiet_thamdinh", ""))
        ws.cell(row=row_num, column=14, value=d.get("gia_thue_sum", ""))
        ws.cell(row=row_num, column=15, value=d.get("hspl", ""))
        ws.cell(row=row_num, column=16, value=d.get("ghi_chu", ""))

        # Highlight missing fields in yellow
        FIELD_TO_COL = {
            'thang': 2, 'ngay_nhan': 3, 'ngay_tra': 4, 'ma_mb': 5,
            'tinh_trang': 6, 'thong_tin_mb': 7, 'tinh': 8, 'dtt': 9,
            'gia_thue_vat': 10, 'bct': 11, 'cv_tkmb': 12,
            'chi_tiet_thamdinh': 13, 'gia_thue_sum': 14, 'hspl': 15,
        }
        for field_name in missing:
            col = FIELD_TO_COL.get(field_name)
            if col:
                ws.cell(row=row_num, column=col).fill = HIGHLIGHT_YELLOW

        # Format date cells
        for col in [3, 4]:
            cell = ws.cell(row=row_num, column=col)
            if cell.value and isinstance(cell.value, datetime):
                cell.number_format = "DD/MM/YYYY"

        written += 1
        if log_callback:
            log_callback(f"✅ Ghi dòng {row_num}: {d.get('ma_mb','')} - {d.get('thong_tin_mb','')[:50]}")

    wb.save(excel_path)
    return written


def rename_file(path, prefix):
    folder = os.path.dirname(path)
    name = os.path.basename(path)
    for p in ["done_", "failed_", "DONE_", "FAILED_"]:
        if name.startswith(p): name = name[len(p):]
    new_path = os.path.join(folder, f"{prefix}_{name}")
    try: os.rename(path, new_path)
    except: pass


# ─── GUI ──────────────────────────────────────────────────────────────────────

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("📧 Email Data Extractor v2.0 – Hybrid AI")
        self.geometry("960x700")
        self.minsize(800, 580)
        self.configure(bg=BG_DARK)
        self._running = False
        self._gemini_initialized = False
        
        self.config_file = os.path.join(FOLDER, "config_tool.json")
        self.email_folder_path = tk.StringVar(value=self._load_saved_folder())
        
        self._build_ui()
        self._scan_files()

    def _load_saved_folder(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, "r") as f:
                    cfg = json.load(f)
                    p = cfg.get("email_folder")
                    if p and os.path.exists(p): return p
        except: pass
        return EMAIL_FOLDER

    def _save_folder(self, path):
        try:
            with open(self.config_file, "w") as f:
                json.dump({"email_folder": path}, f)
        except: pass

    def _browse_folder(self):
        d = filedialog.askdirectory(initialdir=self.email_folder_path.get())
        if d:
            self.email_folder_path.set(d)
            self._save_folder(d)
            self._scan_files()

    def _build_ui(self):
        # ── Header
        hdr = tk.Frame(self, bg=BG_CARD, pady=14)
        hdr.pack(fill="x")
        tk.Label(hdr, text="📧  Email Data Extractor v2.0", font=("Segoe UI", 18, "bold"),
                 bg=BG_CARD, fg=ACCENT2).pack(side="left", padx=20)
        tk.Label(hdr, text="Hybrid: Regex ⚡ + Gemini AI 🤖",
                 font=("Segoe UI", 10), bg=BG_CARD, fg=TEXT_SEC).pack(side="left")

        # ── Body
        body = tk.Frame(self, bg=BG_DARK)
        body.pack(fill="both", expand=True, padx=16, pady=10)

        # Left column
        left = tk.Frame(body, bg=BG_DARK)
        left.pack(side="left", fill="both", expand=True, padx=(0, 8))

        # Folder Browser UI Panel
        dir_frame = tk.Frame(left, bg=BG_CARD, pady=6, padx=10)
        dir_frame.pack(fill="x", pady=(0, 8))
        tk.Label(dir_frame, text="Thư mục Emails:", font=("Segoe UI", 9), bg=BG_CARD, fg=TEXT_SEC).pack(side="left")
        e_fld = tk.Entry(dir_frame, textvariable=self.email_folder_path, bg=BG_PANEL, fg=TEXT_PRI, 
                         bd=0, highlightthickness=1, highlightbackground=BORDER_C)
        e_fld.pack(side="left", fill="x", expand=True, padx=8, ipady=3)
        self._make_btn(dir_frame, "📁 Chọn...", self._browse_folder, bg=ACCENT, fg="white", padx=8, pady=2).pack(side="left")

        fl_hdr = tk.Frame(left, bg=BG_CARD, pady=6, padx=10)
        fl_hdr.pack(fill="x", pady=(0, 4))
        tk.Label(fl_hdr, text="📝 Danh sách .msg", font=("Segoe UI", 10, "bold"),
                 bg=BG_CARD, fg=TEXT_PRI).pack(side="left")
        self.lbl_count = tk.Label(fl_hdr, text="0 file", font=("Segoe UI", 9),
                                   bg=BG_CARD, fg=ACCENT2)
        self.lbl_count.pack(side="right")

        frame_list = tk.Frame(left, bg=BORDER_C)
        frame_list.pack(fill="both", expand=True, pady=(0, 8))
        self.listbox = tk.Listbox(frame_list, bg=BG_PANEL, fg=TEXT_PRI,
                                  selectbackground=ACCENT, selectforeground="white",
                                  font=("Segoe UI", 9), activestyle="none",
                                  relief="flat", bd=0, highlightthickness=0)
        scroll = ttk.Scrollbar(frame_list, orient="vertical", command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=scroll.set)
        self.listbox.pack(side="left", fill="both", expand=True, padx=1, pady=1)
        scroll.pack(side="right", fill="y")

        btn_frame = tk.Frame(left, bg=BG_DARK)
        btn_frame.pack(fill="x")
        self.btn_refresh = self._make_btn(btn_frame, "🔄 Làm mới", self._scan_files, bg=BG_CARD, fg=TEXT_PRI)
        self.btn_refresh.pack(side="left", padx=(0, 8))
        self.btn_run = self._make_btn(btn_frame, "▶  Chạy xử lý", self._start_processing_wrapper, bg=ACCENT, fg="white")
        self.btn_run.pack(side="left")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Custom.Horizontal.TProgressbar", troughcolor=BG_PANEL, background=ACCENT,
                        darkcolor=ACCENT, lightcolor=ACCENT2, bordercolor=BORDER_C, thickness=6)
        self.progress = ttk.Progressbar(left, style="Custom.Horizontal.TProgressbar",
                                        orient="horizontal", mode="determinate")
        self.progress.pack(fill="x", pady=(8, 0))

        # Right column: log
        right = tk.Frame(body, bg=BG_DARK, width=380)
        right.pack(side="right", fill="both", expand=False)
        right.pack_propagate(False)

        log_hdr = tk.Frame(right, bg=BG_CARD, pady=8, padx=10)
        log_hdr.pack(fill="x", pady=(0, 4))
        tk.Label(log_hdr, text="📋 Nhật ký xử lý", font=("Segoe UI", 10, "bold"),
                 bg=BG_CARD, fg=TEXT_PRI).pack(side="left")
        self._make_btn(log_hdr, "🗑 Xóa", self._clear_log,
                       bg=BG_PANEL, fg=TEXT_SEC, padx=6, pady=2).pack(side="right")

        self.log_text = scrolledtext.ScrolledText(right, bg=BG_PANEL, fg=TEXT_PRI,
                                                   font=("Consolas", 8), relief="flat",
                                                   bd=0, state="disabled", wrap="word",
                                                   highlightthickness=0, insertbackground=ACCENT)
        self.log_text.pack(fill="both", expand=True)
        self.log_text.tag_config("ok",   foreground=SUCCESS)
        self.log_text.tag_config("err",  foreground=ERROR_COL)
        self.log_text.tag_config("warn", foreground=WARNING)
        self.log_text.tag_config("info", foreground=ACCENT2)

        # Status bar
        self.status_var = tk.StringVar(value="Sẵn sàng")
        status_bar = tk.Frame(self, bg=BG_CARD, pady=5)
        status_bar.pack(fill="x", side="bottom")
        tk.Label(status_bar, textvariable=self.status_var, font=("Segoe UI", 9),
                 bg=BG_CARD, fg=TEXT_SEC).pack(side="left", padx=16)

        # Gemini status indicator
        gemini_status = "🟢 Gemini OK" if GEMINI_AVAILABLE else "🔴 Gemini N/A"
        tk.Label(status_bar, text=gemini_status, font=("Segoe UI", 9),
                 bg=BG_CARD, fg=SUCCESS if GEMINI_AVAILABLE else ERROR_COL).pack(side="right", padx=16)

    def _make_btn(self, parent, text, cmd, bg=BG_CARD, fg=TEXT_PRI, padx=12, pady=6):
        btn = tk.Button(parent, text=text, command=cmd, bg=bg, fg=fg,
                        font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2",
                        activebackground=ACCENT2, activeforeground="white",
                        padx=padx, pady=pady, bd=0)
        btn.bind("<Enter>", lambda e: btn.config(bg=ACCENT2 if bg == ACCENT else ACCENT))
        btn.bind("<Leave>", lambda e: btn.config(bg=bg))
        return btn

    # ── GEMINI INIT ──────────────────────────────────────────────────────────

    def _start_processing_wrapper(self):
        if GEMINI_AVAILABLE and not self._gemini_initialized:
            self._init_gemini()
        self._start_processing()

    def _init_gemini(self):
        api_key_file = os.path.join(FOLDER, "gemini_api_key.txt")
        api_key = ""
        if os.path.exists(api_key_file):
            with open(api_key_file, "r") as f: api_key = f.read().strip()

        if not api_key:
            api_key = simpledialog.askstring(
                "Cấu hình AI",
                "Nhập API Key Gemini (lấy miễn phí tại aistudio.google.com).\n"
                "Bỏ trống nếu không dùng AI (chỉ xử lý Regex).",
                parent=self)
            if api_key:
                with open(api_key_file, "w") as f: f.write(api_key.strip())

        if api_key:
            try:
                init_gemini(api_key)
                self._log("✅ Đã kích hoạt Gemini AI Vision!", "ok")
            except Exception as e:
                self._log(f"❌ Lỗi Gemini: {e}", "err")
        else:
            self._log("⚠️ Không có API Key - Chỉ dùng Regex.", "warn")

        self._gemini_initialized = True

    # ── ACTIONS ──────────────────────────────────────────────────────────────

    def _scan_files(self):
        self.listbox.delete(0, "end")
        current_dir = self.email_folder_path.get()
        if not current_dir or not os.path.exists(current_dir):
            self.status_var.set("⚠️ Thư mục email không hợp lệ.")
            return
        pattern = os.path.join(current_dir, "*.msg")
        all_files = [f for f in glob.glob(pattern) if not os.path.basename(f).startswith("~$")]

        new_files, done_files, failed_files = [], [], []
        for f in all_files:
            bn = os.path.basename(f).lower()
            if bn.startswith("done_"): done_files.append(f)
            elif bn.startswith("failed_"): failed_files.append(f)
            else: new_files.append(f)

        for f in new_files:
            self.listbox.insert("end", "  ⏳ " + os.path.basename(f))
            self.listbox.itemconfig("end", fg=TEXT_PRI)
        for f in done_files:
            self.listbox.insert("end", "  ✅ " + os.path.basename(f))
            self.listbox.itemconfig("end", fg=SUCCESS)
        for f in failed_files:
            self.listbox.insert("end", "  ❌ " + os.path.basename(f))
            self.listbox.itemconfig("end", fg=ERROR_COL)

        self.lbl_count.config(text=f"{len(new_files)} chờ / {len(all_files)} file")
        self._log(f"🔍 {len(new_files)} chờ, {len(done_files)} done, {len(failed_files)} failed", "info")
        self.status_var.set(f"{len(new_files)} chờ | {len(done_files)} done | {len(failed_files)} failed")

    def _clear_log(self):
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.configure(state="disabled")

    def _log(self, msg, tag=""):
        self.log_text.configure(state="normal")
        ts = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert("end", f"[{ts}] {msg}\n", tag)
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def _start_processing(self):
        if self._running: return
        target_dir = self.email_folder_path.get()
        if not target_dir or not os.path.exists(target_dir):
            messagebox.showerror("Lỗi", "Thư mục email hiện tại không tồn tại!")
            return
        pattern = os.path.join(target_dir, "*.msg")
        files = [f for f in glob.glob(pattern)
                 if not os.path.basename(f).startswith("~$")
                 and not os.path.basename(f).lower().startswith("done_")
                 and not os.path.basename(f).lower().startswith("failed_")]
        if not files:
            messagebox.showinfo("Thông báo", "Không có file .msg nào để xử lý.")
            return

        excel_path = os.path.join(FOLDER, EXCEL_NAME)
        if not os.path.exists(excel_path):
            messagebox.showerror("Lỗi", f"Không tìm thấy:\n{excel_path}")
            return

        self._running = True
        self.btn_run.config(state="disabled", text="⏳ Đang xử lý...")
        self.progress["maximum"] = len(files)
        self.progress["value"] = 0

        thread = threading.Thread(target=self._run_processing, args=(files, excel_path), daemon=True)
        thread.start()

    def _run_processing(self, files, excel_path):
        results = []
        done_count, partial_count, fail_count = 0, 0, 0

        for i, f in enumerate(files):
            self._log(f"📨 [{i+1}/{len(files)}] {os.path.basename(f)}", "info")
            self.status_var.set(f"Xử lý {i+1}/{len(files)}: {os.path.basename(f)[:40]}...")

            result = process_msg_file(f, log_callback=self._log)
            results.append(result)

            if result["success"] and not result.get("partial"):
                done_count += 1
            elif result["success"] and result.get("partial"):
                partial_count += 1
            else:
                fail_count += 1
                self._log(f"❌ Lỗi: {result['error']}", "err")

            self.progress["value"] = i + 1

        # Write ALL successful results to Excel (including partial)
        try:
            success_results = [r for r in results if r["success"]]
            if success_results:
                self._log(f"\n💾 Đang ghi {len(success_results)} dòng vào Excel...", "info")
                written = write_to_excel(success_results, excel_path, self._log)
                self._log(f"✅ Đã ghi {written} dòng vào Excel!", "ok")
        except Exception as e:
            self._log(f"❌ Lỗi ghi Excel: {e}", "err")

        # ── BƯỚC 3: Rename files based on completeness ──
        for r in results:
            if not r["success"]:
                rename_file(r["path"], "failed")
            else:
                # Cả hoàn chỉnh 100% và thành công 1 phần (partial) đều đánh dấu Done
                rename_file(r["path"], "done")

        # Summary
        self._log("\n" + "═"*45, "info")
        self._log("📊 TỔNG KẾT:", "info")
        self._log(f"   ✅ Hoàn chỉnh (done): {done_count}/{len(files)}", "ok")
        if partial_count:
            self._log(f"   ⚠️ Thiếu dữ liệu (failed): {partial_count}/{len(files)}", "warn")
            for r in results:
                if r.get("partial"):
                    missing = ", ".join(r.get("missing_fields", []))
                    self._log(f"      • {r['file']}: [{missing}]", "warn")
        if fail_count:
            self._log(f"   ❌ Không xử lý được: {fail_count}/{len(files)}", "err")
            for r in results:
                if not r["success"]:
                    self._log(f"      • {r['file']}: {r['error']}", "err")
        self._log("═"*45, "info")

        self.status_var.set(f"Xong: {done_count} done | {partial_count} thiếu | {fail_count} lỗi")
        self.btn_run.config(state="normal", text="▶  Chạy xử lý")
        self._running = False
        self._scan_files()

        total_ok = done_count + partial_count
        if partial_count or fail_count:
            messagebox.showwarning("Hoàn thành",
                f"✅ Hoàn chỉnh: {done_count} file\n"
                f"⚠️ Thiếu dữ liệu: {partial_count} file\n"
                f"❌ Không xử lý: {fail_count} file\n\n"
                "Các ô thiếu đã được tô vàng trong Excel.")
        else:
            messagebox.showinfo("Hoàn thành",
                f"✅ Xử lý thành công {done_count} file!\nDữ liệu đã ghi vào {EXCEL_NAME}")

        # Tự động mở file Excel
        try:
            excel_path = os.path.join(FOLDER, EXCEL_NAME)
            os.startfile(excel_path)
            self._log(f"📂 Đã tự động mở file {EXCEL_NAME}", "ok")
        except Exception as e:
            self._log(f"❌ Không thể mở file Excel: {e}", "err")


if __name__ == "__main__":
    app = App()
    app.mainloop()
