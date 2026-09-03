"""Screenshot Annotation & Full-Page Visual Header Renderer.

Draws rich execution details (Step Description, Current URL, Timestamp, Test Name)
directly onto captured screenshot image files using Pillow (PIL).
"""

from datetime import datetime
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


def annotate_screenshot_with_details(
    image_path: str,
    step_description: str,
    url: str = "",
    test_name: str = "",
    status: str = "PASSED"
) -> str:
    """Draws a professional dark metadata header banner directly onto the screenshot image."""
    try:
        path = Path(image_path)
        if not path.exists():
            return image_path

        orig_img = Image.open(path).convert("RGB")
        orig_width, orig_height = orig_img.size

        # Create header banner canvas (height: 60px)
        header_height = 60
        new_height = orig_height + header_height
        annotated_img = Image.new("RGB", (orig_width, new_height), color=(15, 23, 42))  # Slate dark #0f172a

        # Paste original image below the header
        annotated_img.paste(orig_img, (0, header_height))

        draw = ImageDraw.Draw(annotated_img)

        # Draw status indicator box on top-left
        draw.rectangle([10, 10, 85, 50], fill=(34, 197, 94) if status == "PASSED" else (239, 68, 68))
        draw.text((20, 22), status, fill=(255, 255, 255))

        # Format details text
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        step_line = f"STEP: {step_description[:80]}"
        url_line = f"URL: {url[:70]}" if url else ""
        test_line = f"TEST: {test_name[:50]}" if test_name else ""

        # Draw details text
        draw.text((100, 12), step_line, fill=(255, 255, 255))
        if url_line:
            draw.text((100, 34), url_line, fill=(148, 163, 184))  # Slate light #94a3b8

        # Draw timestamp and test name on right
        time_text = f"TIME: {now_str}"
        draw.text((max(100, orig_width - 240), 12), time_text, fill=(253, 224, 71))  # Yellow #fde047
        if test_line:
            draw.text((max(100, orig_width - 240), 34), test_line, fill=(192, 132, 252))  # Purple #c084fc

        annotated_img.save(path, format="PNG")
        return str(path)
    except Exception as e:
        print(f"Failed to annotate screenshot {image_path}: {e}")
        return image_path
