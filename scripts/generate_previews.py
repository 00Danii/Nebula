import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from core.engine import RenderEngine
from PIL import Image

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "examples")
SUBJECT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "Nebula.png")
os.makedirs(OUTPUT_DIR, exist_ok=True)

STYLES = [
    ("sepia", "Sepia"),
    ("crt", "CRT"),
    ("thermal", "Thermal"),
    ("noir", "Noir"),
    ("cyberpunk", "Cyberpunk"),
    ("vaporwave", "Vaporwave"),
    ("gold", "Gold"),
    ("ice", "Ice"),
    ("pastel", "Pastel"),
    ("muted", "Muted"),
    ("invert", "Invert"),
    ("neon", "Neon"),
    ("duotone", "Duotone"),
    ("tritone", "Tritone"),
    ("alien_signal", "Alien Signal"),
    ("custom", "Custom"),
]

engine = RenderEngine()
engine.set_display_config("show_metadata", True)
engine.set_display_config("metadata_style", "minimal")
engine.set_display_config("grid_num_lines", 6)
engine.set_display_config("font_size_main", 18)
engine.set_display_config("font_size_small", 15)
engine.set_display_config("meta_font_size", 14)

for style_id, style_name in STYLES:
    print(f"Rendering {style_name}...")
    engine.set_style(style_id)
    try:
        result = engine.render(SUBJECT_PATH)
        filename = f"{style_id}.png"
        filepath = os.path.join(OUTPUT_DIR, filename)
        result.save(filepath)
        print(f"  -> saved {filepath}")
    except Exception as e:
        print(f"  -> ERROR: {e}")
