"""
Visual Layout Diff Engine for Kirki eCommerce Automation Suite
Provides baseline image comparison, pixel-by-pixel diffing, and red-highlight visual diff image generation.
"""

import os
from PIL import Image, ImageChops, ImageEnhance, ImageDraw


BASELINES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "baselines")
DIFFS_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "reports", "visual_diffs"))


def ensure_dirs():
    """Ensure baseline and diff output directories exist."""
    os.makedirs(BASELINES_DIR, exist_ok=True)
    os.makedirs(DIFFS_DIR, exist_ok=True)


def compare_images(baseline_path: str, current_path: str, diff_output_path: str, threshold: float = 0.02) -> dict:
    """
    Compares two images pixel-by-pixel.
    Generates a red-tinted diff image if changes exceed threshold.
    
    Returns dict:
        {
            "passed": bool,
            "diff_ratio": float,
            "diff_path": str or None,
            "message": str
        }
    """
    ensure_dirs()

    if not os.path.exists(baseline_path):
        # Save current as baseline if none exists
        img = Image.open(current_path)
        img.save(baseline_path)
        return {
            "passed": True,
            "diff_ratio": 0.0,
            "diff_path": None,
            "message": f"Baseline created at {baseline_path}"
        }

    img1 = Image.open(baseline_path).convert("RGB")
    img2 = Image.open(current_path).convert("RGB")

    # Resize img2 to match img1 if dimensions differ slightly due to scrollbar/rendering
    if img1.size != img2.size:
        img2 = img2.resize(img1.size, Image.Resampling.LANCZOS)

    # Compute absolute difference
    diff = ImageChops.difference(img1, img2)
    gray_diff = diff.convert("L")

    # Count pixels that differ noticeably
    threshold_value = 25  # pixel brightness difference tolerance
    diff_pixels = sum(1 for pixel in gray_diff.getdata() if pixel > threshold_value)
    total_pixels = img1.width * img1.height
    diff_ratio = diff_pixels / float(total_pixels)

    passed = diff_ratio <= threshold

    if not passed:
        # Create visual diff image with red highlights
        mask = gray_diff.point(lambda p: 255 if p > threshold_value else 0)
        
        # Dim original image
        enhancer = ImageEnhance.Brightness(img2)
        dimmed = enhancer.enhance(0.4)
        
        # Create red overlay mask
        red_overlay = Image.new("RGB", img1.size, (255, 0, 0))
        diff_image = Image.composite(red_overlay, dimmed, mask)
        
        # Draw metadata header on diff image
        draw = ImageDraw.Draw(diff_image)
        header_text = f"VISUAL DIFF DETECTED | Discrepancy: {diff_ratio:.2%} (Threshold: {threshold:.2%})"
        draw.rectangle([(0, 0), (img1.width, 30)], fill=(220, 38, 38))
        draw.text((15, 7), header_text, fill=(255, 255, 255))
        
        diff_image.save(diff_output_path)

    return {
        "passed": passed,
        "diff_ratio": round(diff_ratio, 4),
        "diff_path": diff_output_path if not passed else None,
        "message": f"Diff ratio: {diff_ratio:.2%}" if passed else f"Visual layout regression detected! Diff ratio: {diff_ratio:.2%} > threshold ({threshold:.2%})"
    }
