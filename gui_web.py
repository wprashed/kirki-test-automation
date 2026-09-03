"""Kirki eCommerce Test Automation Studio — Flask backend only."""

import subprocess
import sys
import threading
import time
from pathlib import Path

from flask import Flask, Response, jsonify, request, send_from_directory

from reports.report_generator import generate_qa_report, generate_summary_report

BASE_DIR      = Path(__file__).resolve().parent
STATIC_DIR    = BASE_DIR / "static"
LOG_FILE      = BASE_DIR / "reports" / "gui_run.log"
SCREENSHOTS_DIR = BASE_DIR / "reports" / "screenshots"
HISTORY_DIR   = BASE_DIR / "reports" / "history"

app = Flask(__name__, static_folder=str(STATIC_DIR), static_url_path="/static")

run_state = {
    "is_running": False,
    "process":    None,
}


# ── Main SPA ──────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    """Serve the pre-built HTML dashboard."""
    return send_from_directory(STATIC_DIR, "index.html")


# ── Run ───────────────────────────────────────────────────────────────────────

@app.route("/api/run", methods=["POST"])
def api_run():
    # If a real process is still alive, reject
    if run_state["is_running"]:
        proc = run_state.get("process")
        if proc and proc.poll() is None:
            return jsonify({"status": "already_running"})
        run_state["is_running"] = False

    data     = request.get_json(silent=True) or {}
    suite    = data.get("suite", "all")
    headless = data.get("headless", True)   # False = live browser window

    # Prepare log immediately so the stream endpoint has something to open
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    mode_label = "headless" if headless else "LIVE BROWSER"
    LOG_FILE.write_text(
        f"=== Kirki Test Suite Starting [suite={suite}] [mode={mode_label}] ===\n",
        encoding="utf-8",
    )
    run_state["is_running"] = True

    def _execute():
        venv_python = BASE_DIR / ".venv" / "bin" / "python3"
        python_bin = str(venv_python) if venv_python.exists() else sys.executable
        cmd = [python_bin, "-m", "pytest"]
        suite_map = {
            "smoke":          "tests/smoke/",
            "admin":          "tests/admin/",
            "coupons":        "tests/coupons/",
            "frontend":       "tests/frontend/",
            "orders":         "tests/orders/",
            "security":       "tests/security/",
            "visual":         "tests/visual/",
            "visual_diff":    "tests/visual/test_visual_layout_diff_regression.py",
            "web_vitals":     "tests/performance/test_core_web_vitals_audit.py",
            "security_dast":  "tests/security/test_dast_vulnerability_scanner.py",
            "ui_walkthrough": "tests/ui_walkthrough/",
            "performance":    "tests/performance/",
            "all":            "tests/",
        }
        cmd.append(suite_map.get(suite, "tests/"))
        cmd += ["-v",
                f"--html={BASE_DIR / 'reports' / 'latest_report.html'}",
                "--self-contained-html"]

        if data.get("parallel", False):
            cmd.extend(["-n", "4"])

        # Propagate headless flag via env so conftest.py / settings pick it up
        import os as _os
        env = dict(_os.environ)
        env["HEADLESS"] = "false" if not headless else "true"

        try:
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=str(BASE_DIR),
                env=env,
            )
            run_state["process"] = proc
            with LOG_FILE.open("a", encoding="utf-8") as fh:
                for line in proc.stdout:
                    fh.write(line)
                    fh.flush()
            proc.wait()
        except Exception as exc:
            with LOG_FILE.open("a", encoding="utf-8") as fh:
                fh.write(f"\nFATAL: {exc}\n")

        try:
            log_text = LOG_FILE.read_text(encoding="utf-8", errors="ignore")
            stats = get_real_stats()
            lr = stats["last_run"]
            passed = lr["passed"]
            failed = lr["failed"]
            total = lr["total"] or stats["total_available_tests"]
            dur_str = lr["duration"].rstrip("s") if isinstance(lr["duration"], str) else "0"
            try:
                dur = float(dur_str)
            except ValueError:
                dur = 0.0
            generate_summary_report(total, passed, failed, dur, log_text)
            generate_qa_report(log_text, total, passed, failed, dur)
        except Exception:
            pass

        run_state["is_running"] = False

    threading.Thread(target=_execute, daemon=True).start()
    return jsonify({"status": "started"})


@app.route("/api/abort", methods=["POST"])
def api_abort():
    """Abort currently running pytest process immediately."""
    proc = run_state.get("process")
    if proc:
        try:
            proc.terminate()
            time.sleep(0.3)
            if proc.poll() is None:
                proc.kill()
        except Exception:
            pass

    run_state["is_running"] = False
    run_state["process"] = None

    if LOG_FILE.exists():
        with LOG_FILE.open("a", encoding="utf-8") as fh:
            fh.write("\n\n⚠️ TEST EXECUTION ABORTED BY USER.\n")

    return jsonify({"status": "aborted"})


# ── Statistics API ─────────────────────────────────────────────────────────────

def get_real_stats():
    """Scans codebase for total available tests and parses latest run log dynamically."""
    import re
    tests_dir = BASE_DIR / "tests"
    suite_counts = {}
    total_available = 0
    if tests_dir.exists():
        for suite_dir in tests_dir.iterdir():
            if suite_dir.is_dir() and not suite_dir.name.startswith("__"):
                c = 0
                for py_file in suite_dir.glob("*.py"):
                    if py_file.name not in ("__init__.py", "conftest.py"):
                        try:
                            txt = py_file.read_text(encoding="utf-8", errors="ignore")
                            c += txt.count("def test_")
                        except Exception:
                            pass
                if c > 0:
                    suite_counts[suite_dir.name] = c
                    total_available += c

    last_run = {
        "has_run": False,
        "passed": 0,
        "failed": 0,
        "total": 0,
        "pass_rate": "N/A",
        "duration": "N/A",
        "status": "Not run yet"
    }

    if LOG_FILE.exists():
        log_text = LOG_FILE.read_text(encoding="utf-8", errors="ignore")
        if log_text.strip():
            last_run["has_run"] = True
            match = re.search(r"=+\s+(.*?)\s+in\s+([\d\.]+s)", log_text)
            if match:
                summary_line = match.group(1)
                last_run["duration"] = match.group(2)
                p_match = re.search(r"(\d+)\s+passed", summary_line)
                f_match = re.search(r"(\d+)\s+failed", summary_line)
                passed = int(p_match.group(1)) if p_match else 0
                failed = int(f_match.group(1)) if f_match else 0
                total = passed + failed
                last_run["passed"] = passed
                last_run["failed"] = failed
                last_run["total"] = total
                if total > 0:
                    rate = int(round((passed / total) * 100))
                    last_run["pass_rate"] = f"{rate}%"
                else:
                    last_run["pass_rate"] = "100%"
                last_run["status"] = "Passed" if failed == 0 else "Failed"

    shot_count = len(list(SCREENSHOTS_DIR.glob("*.png"))) if SCREENSHOTS_DIR.exists() else 0

    return {
        "total_available_tests": total_available,
        "suite_counts": suite_counts,
        "last_run": last_run,
        "screenshot_count": shot_count,
    }


@app.route("/api/stats")
def api_stats():
    return jsonify(get_real_stats())


# ── Live stream ───────────────────────────────────────────────────────────────

@app.route("/api/stream")
def api_stream():
    def _generate():
        # Ensure log file exists
        if not LOG_FILE.exists():
            LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
            LOG_FILE.write_text(
                "=== Kirki Test Automation Studio Ready ===\nClick 'Run Selected Suite' to execute automated tests.\n",
                encoding="utf-8"
            )

        with LOG_FILE.open("r", encoding="utf-8") as fh:
            while True:
                line = fh.readline()
                if line:
                    # SSE data lines must not contain bare newlines
                    yield "data: " + line.rstrip("\n") + "\n\n"
                else:
                    if not run_state["is_running"]:
                        yield "data: [DONE]\n\n"
                        return
                    time.sleep(0.25)

    return Response(_generate(), mimetype="text/event-stream",
                    headers={"X-Accel-Buffering": "no",
                             "Cache-Control": "no-cache"})


# ── Static assets ─────────────────────────────────────────────────────────────

@app.route("/api/clear/<target>", methods=["POST"])
def api_clear(target):
    """Delete files inside screenshots/, history/, or the latest reports."""
    deleted = 0
    
    if target in ("screenshots", "all"):
        if SCREENSHOTS_DIR.exists():
            for f in SCREENSHOTS_DIR.glob("*.*"):
                try:
                    f.unlink()
                    deleted += 1
                except Exception:
                    pass

    if target in ("history", "all"):
        if HISTORY_DIR.exists():
            for f in HISTORY_DIR.glob("*.html"):
                try:
                    f.unlink()
                    deleted += 1
                except Exception:
                    pass

    if target in ("reports", "all"):
        reports_dir = BASE_DIR / "reports"
        if reports_dir.exists():
            for pattern in ["*.html", "*.log", "*.txt"]:
                for f in reports_dir.glob(pattern):
                    try:
                        f.unlink()
                        deleted += 1
                    except Exception:
                        pass
        # Re-initialize LOG_FILE so stream endpoint is ready
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        LOG_FILE.write_text(
            "=== Kirki Test Automation Studio Data Cleared ===\nReady for next test run.\n",
            encoding="utf-8"
        )

    return jsonify({"status": "ok", "target": target, "deleted": deleted})


@app.route("/api/screenshots")
def api_screenshots():
    if not SCREENSHOTS_DIR.exists():
        return jsonify([])
    files = sorted([f.name for f in SCREENSHOTS_DIR.glob("*.png")], reverse=True)
    return jsonify(files)


@app.route("/api/history")
def api_history():
    if not HISTORY_DIR.exists():
        return jsonify([])
    files = sorted([f.name for f in HISTORY_DIR.glob("*.html")], reverse=True)
    return jsonify(files)


@app.route("/screenshots/<path:filename>")
def serve_screenshot(filename):
    return send_from_directory(SCREENSHOTS_DIR, filename)


@app.route("/history/<path:filename>")
def serve_history(filename):
    return send_from_directory(HISTORY_DIR, filename)


# ── Reports ───────────────────────────────────────────────────────────────────

@app.route("/report")
def report():
    f = BASE_DIR / "reports" / "latest_report.html"
    if not f.exists():
        f = BASE_DIR / "reports" / "report.html"
    if f.exists():
        return Response(f.read_bytes(), mimetype="text/html")
    return """<!DOCTYPE html><html class="dark"><head><script src="https://cdn.tailwindcss.com"></script><style>body{background-color:#0B0F19;color:#F1F5F9;font-family:sans-serif;}</style></head>
    <body class="flex items-center justify-center min-h-screen p-8">
        <div class="p-8 rounded-3xl bg-slate-900 border border-slate-800 text-center max-w-md space-y-3">
            <h2 class="text-xl font-black text-white">No Test Report Available</h2>
            <p class="text-slate-400 text-xs">Run a test suite from the Web Automation Studio or CLI to generate execution reports.</p>
        </div>
    </body></html>""", 200


@app.route("/qa-report")
def qa_report():
    qa_file = BASE_DIR / "reports" / "qa_report.html"
    if not qa_file.exists():
        if LOG_FILE.exists() and LOG_FILE.read_text(encoding="utf-8", errors="ignore").strip():
            log_text = LOG_FILE.read_text(encoding="utf-8", errors="ignore")
            generate_qa_report(log_text)
        else:
            return """<!DOCTYPE html><html class="dark"><head><script src="https://cdn.tailwindcss.com"></script><style>body{background-color:#0B0F19;color:#F1F5F9;font-family:sans-serif;}</style></head>
            <body class="flex items-center justify-center min-h-screen p-8">
                <div class="p-8 rounded-3xl bg-slate-900 border border-slate-800 text-center max-w-md space-y-3">
                    <h2 class="text-xl font-black text-white">No QA Report Data</h2>
                    <p class="text-slate-400 text-xs">Run a test suite from the Web Automation Studio or CLI to generate a live QA report.</p>
                </div>
            </body></html>""", 200
    if qa_file.exists():
        return Response(qa_file.read_bytes(), mimetype="text/html")
    return "<h1 style='font-family:sans-serif;padding:2rem'>No QA report available.</h1>", 404


# ── Entry ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=== Kirki Test Automation Studio ===")
    print(f"    Open http://localhost:5001  in your browser")
    app.run(host="0.0.0.0", port=5001, debug=False, threaded=True)
