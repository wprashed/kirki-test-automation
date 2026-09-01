"""Visual Regression and Screenshot Pixel Diff Utility using Pillow."""

import os
from pathlib import Path
from PIL import Image, ImageChops

REPORTS_DIR = Path(__file__).resolve().parent.parent.parent / "reports"
BASELINE_DIR = REPORTS_DIR / "visual_baseline"
SCREENSHOT_DIR = REPORTS_DIR / "screenshots"
DIFF_DIR = REPORTS_DIR / "visual_diffs"

def ensure_visual_dirs():
    BASELINE_DIR.mkdir(parents=True, exist_ok=True)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    DIFF_DIR.mkdir(parents=True, exist_ok=True)

def compare_screenshot_with_baseline(driver, page_name: str, threshold: float = 0.05) -> dict:
    """Capture page screenshot and compare against baseline image."""
    ensure_visual_dirs()
    
    current_path = SCREENSHOT_DIR / f"{page_name}_current.png"
    baseline_path = BASELINE_DIR / f"{page_name}_baseline.png"
    diff_path = DIFF_DIR / f"{page_name}_diff.png"

    driver.save_screenshot(str(current_path))

    if not baseline_path.exists():
        # Save baseline if first run
        driver.save_screenshot(str(baseline_path))
        return {"status": "BASELINE_CREATED", "diff_ratio": 0.0, "message": f"Created baseline for {page_name}"}

    img_current = Image.open(current_path).convert("RGB")
    img_baseline = Image.open(baseline_path).convert("RGB")

    # Resize if window dimensions differ slightly
    if img_current.size != img_baseline.size:
        img_current = img_current.resize(img_baseline.size)

    diff = ImageChops.difference(img_current, img_baseline)
    bbox = diff.getbbox()

    if bbox is None:
        return {"status": "MATCH", "diff_ratio": 0.0, "message": "Visual match 100%"}

    # Calculate difference ratio
    stat = diff.histogram()
    diff_pixels = sum(stat[1:])
    total_pixels = img_current.size[0] * img_current.size[1] * 3
    diff_ratio = diff_pixels / float(total_pixels)

    if diff_ratio > threshold:
        diff.save(str(diff_path))
        return {
            "status": "MISMATCH",
            "diff_ratio": diff_ratio,
            "diff_path": str(diff_path),
            "message": f"Visual mismatch detected ({diff_ratio*100:.2f}% diff)"
        }

    return {"status": "MATCH", "diff_ratio": diff_ratio, "message": "Visual regression within threshold"}
