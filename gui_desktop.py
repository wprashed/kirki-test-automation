"""Desktop Native GUI for Kirki eCommerce Test Automation using Tkinter."""

import sys
import subprocess
import threading
import os
import webbrowser
from pathlib import Path

try:
    import tkinter as tk
    from tkinter import ttk, scrolledtext, messagebox
except ImportError:
    print("Tkinter is required for Desktop GUI.")
    sys.exit(1)

BASE_DIR = Path(__file__).resolve().parent

class KirkiTestRunnerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Kirki eCommerce Test Automation Runner")
        self.root.geometry("800x600")
        self.root.configure(bg="#0F172A")

        # Styling
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TLabel", background="#0F172A", foreground="#F8FAFC", font=("Helvetica", 10))
        style.configure("TFrame", background="#0F172A")
        style.configure("THeader.TLabel", font=("Helvetica", 14, "bold"), foreground="#FFFFFF")
        style.configure("TButton", font=("Helvetica", 10, "bold"), padding=6)

        # Header Frame
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill="x", px=20, py=15)
        
        lbl_title = ttk.Label(header_frame, text="Kirki eCommerce Test Automation", style="THeader.TLabel")
        lbl_title.pack(anchor="w")
        lbl_subtitle = ttk.Label(header_frame, text="Execute pytest suites and view real-time logs & reports")
        lbl_subtitle.pack(anchor="w")

        # Controls Frame
        controls_frame = ttk.LabelFrame(self.root, text=" Test Configuration ", padding=15)
        controls_frame.pack(fill="x", px=20, py=10)

        # Suite Selector
        ttk.Label(controls_frame, text="Select Test Suite:").grid(row=0, column=0, sticky="w", py=5)
        self.suite_var = tk.StringVar(value="smoke")
        suite_cb = ttk.Combobox(controls_frame, textvariable=self.suite_var, state="readonly", width=25)
        suite_cb["values"] = ("smoke", "admin", "coupons", "security", "all")
        suite_cb.grid(row=0, column=1, sticky="w", px=10, py=5)

        # Headless Checkbox
        self.headless_var = tk.BooleanVar(value=True)
        headless_chk = ttk.Checkbutton(controls_frame, text="Run Headless (Hidden Browser)", variable=self.headless_var)
        headless_chk.grid(row=0, column=2, sticky="w", px=10, py=5)

        # Buttons
        btn_frame = ttk.Frame(controls_frame)
        btn_frame.grid(row=1, column=0, columnspan=3, sticky="we", py=10)

        self.btn_run = ttk.Button(btn_frame, text="🚀 Run Tests", command=self.start_tests)
        self.btn_run.pack(side="left", px=5)

        self.btn_report = ttk.Button(btn_frame, text="📊 Open HTML Report", command=self.open_report)
        self.btn_report.pack(side="left", px=5)

        self.btn_qa = ttk.Button(btn_frame, text="❓ Open Q&A Report", command=self.open_qa_report)
        self.btn_qa.pack(side="left", px=5)

        # Output Console Frame
        console_frame = ttk.LabelFrame(self.root, text=" Execution Output Console ", padding=10)
        console_frame.pack(fill="both", expand=True, px=20, py=10)

        self.console = scrolledtext.ScrolledText(console_frame, bg="#020617", fg="#38BDF8", font=("Courier", 10))
        self.console.pack(fill="both", expand=True)

    def log(self, text):
        self.console.insert(tk.END, text)
        self.console.see(tk.END)

    def start_tests(self):
        self.btn_run.config(state="disabled")
        self.console.delete("1.0", tk.END)
        self.log(f"Starting test suite: {self.suite_var.get()}...\n\n")

        thread = threading.Thread(target=self.run_pytest, daemon=True)
        thread.start()

    def run_pytest(self):
        suite = self.suite_var.get()
        cmd = [sys.executable, "-m", "pytest"]
        
        if suite == "smoke":
            cmd.append("tests/smoke/")
        elif suite == "admin":
            cmd.append("tests/admin/")
        elif suite == "coupons":
            cmd.append("tests/coupons/")
        elif suite == "security":
            cmd.append("tests/security/")
        elif suite == "all":
            cmd.append("tests/")

        cmd.extend(["-v", f"--html={BASE_DIR}/reports/latest_report.html", "--self-contained-html"])

        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, cwd=str(BASE_DIR))
        for line in proc.stdout:
            self.root.after(0, self.log, line)
        proc.wait()

        self.root.after(0, self.finish_tests, proc.returncode)

    def finish_tests(self, returncode):
        self.btn_run.config(state="normal")
        status = "PASSED" if returncode == 0 else "FAILED"
        self.log(f"\nTest Execution Finished. Final Status: {status}\n")

    def open_report(self):
        report_path = BASE_DIR / "reports" / "latest_report.html"
        if report_path.exists():
            webbrowser.open(f"file://{report_path}")
        else:
            messagebox.showinfo("Report Not Found", "No test report generated yet. Run tests first!")

    def open_qa_report(self):
        report_path = BASE_DIR / "reports" / "qa_report.html"
        if not report_path.exists():
            from reports.report_generator import generate_qa_report
            generate_qa_report()
        webbrowser.open(f"file://{report_path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = KirkiTestRunnerApp(root)
    root.mainloop()
