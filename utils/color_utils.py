import numpy as np
from PIL import Image


def apply_sepia_tone(image: Image.Image, intensity: float = 1.0) -> Image.Image:
    img_array = np.array(image.convert("RGB"), dtype=np.float32)
    sepia_matrix = np.array([
        [0.393, 0.769, 0.189],
        [0.349, 0.686, 0.168],
        [0.272, 0.534, 0.131]
    ])
    sepia = img_array @ sepia_matrix.T
    sepia = np.clip(sepia * intensity, 0, 255).astype(np.uint8)
    return Image.fromarray(sepia)


def apply_thermal_palette(image: Image.Image) -> Image.Image:
    gray = image.convert("L")
    gray_array = np.array(gray, dtype=np.float32)
    normalized = gray_array / 255.0

    def thermal_map(v):
        r = np.clip(4.0 * v - 1.0, 0.0, 1.0) * 2.0
        g = np.clip(4.0 * v - 2.0, 0.0, 1.0) * 2.0 if v < 0.5 else np.clip(-4.0 * v + 4.0, 0.0, 1.0)
        b = np.clip(-4.0 * v + 3.0, 0.0, 1.0) * 2.0 if v > 0.25 else 1.0
        return np.clip(r, 0, 1), np.clip(g, 0, 1), np.clip(b, 0, 1)

    r_ch = np.zeros_like(normalized)
    g_ch = np.zeros_like(normalized)
    b_ch = np.zeros_like(normalized)

    for i in range(3):
        channel = [r_ch, g_ch, b_ch][i]
        if i == 0:
            channel[:] = np.clip(4.0 * normalized - 1.0, 0.0, 1.0) * 2.0
        elif i == 1:
            mask1 = normalized < 0.5
            mask2 = normalized >= 0.5
            channel[mask1] = np.clip(4.0 * normalized[mask1] - 2.0, 0.0, 1.0) * 2.0
            channel[mask2] = np.clip(-4.0 * normalized[mask2] + 4.0, 0.0, 1.0)
        else:
            mask = normalized > 0.25
            channel[~mask] = 1.0
            channel[mask] = np.clip(-4.0 * normalized[mask] + 3.0, 0.0, 1.0) * 2.0

    thermal = np.stack([
        np.clip(r_ch * 255, 0, 255),
        np.clip(g_ch * 255, 0, 255),
        np.clip(b_ch * 255, 0, 255)
    ], axis=2).astype(np.uint8)

    return Image.fromarray(thermal)


def blend_with_alpha(base: np.ndarray, overlay: np.ndarray, alpha: float) -> np.ndarray:
    return (base * (1 - alpha) + overlay * alpha).astype(np.uint8)
