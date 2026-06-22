import cv2
import numpy as np
from PIL import Image, ImageEnhance


class ImageProcessor:
    def load(self, path: str) -> Image.Image:
        img = cv2.imread(path)
        if img is None:
            raise FileNotFoundError(f"No se pudo cargar la imagen: {path}")
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        return Image.fromarray(img_rgb)

    def enhance_contrast(self, image: Image.Image, clip_limit: float = 2.0, grid_size: int = 8) -> Image.Image:
        arr = np.array(image.convert("RGB"), dtype=np.uint8)
        hsv = cv2.cvtColor(arr, cv2.COLOR_RGB2HSV).astype(np.uint8)
        clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(grid_size, grid_size))
        hsv[:, :, 2] = clahe.apply(hsv[:, :, 2])
        return Image.fromarray(cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB))

    def create_canvas(self, size: tuple[int, int], background: tuple[int, int, int] = (0, 0, 0)) -> Image.Image:
        return Image.new("RGB", size, background)

    def apply_adjustments(self, image: Image.Image, adj: dict) -> Image.Image:
        img = image.convert("RGB")

        b = adj.get("brightness", 0)
        if b != 0:
            val = (b + 100) / 100
            img = ImageEnhance.Brightness(img).enhance(val)

        c = adj.get("contrast", 0)
        if c != 0:
            val = (c + 100) / 100
            img = ImageEnhance.Contrast(img).enhance(val)

        s = adj.get("saturation", 0)
        if s != 0:
            val = (s + 100) / 100
            img = ImageEnhance.Color(img).enhance(val)

        sh = adj.get("sharpness", 0)
        if sh != 0:
            val = (sh + 100) / 100
            img = ImageEnhance.Sharpness(img).enhance(val)

        h = adj.get("hue", 0)
        if h != 0:
            arr = np.array(img, dtype=np.uint8)
            hsv = cv2.cvtColor(arr, cv2.COLOR_RGB2HSV).astype(np.int32)
            shift = int(round(h * 0.9))
            hsv[:, :, 0] = (hsv[:, :, 0] + shift) % 180
            img = Image.fromarray(cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB))

        g = adj.get("gamma", 1.0)
        if g != 1.0:
            arr = np.array(img, dtype=np.float32) / 255.0
            arr = np.power(np.clip(arr, 0, 1), 1.0 / g)
            img = Image.fromarray(np.clip(arr * 255, 0, 255).astype(np.uint8))

        t = adj.get("temperature", 0)
        if t != 0:
            arr = np.array(img, dtype=np.float32)
            factor = t / 100.0
            arr[:, :, 0] = np.clip(arr[:, :, 0] * (1 + factor * 0.15), 0, 255)
            arr[:, :, 2] = np.clip(arr[:, :, 2] * (1 - factor * 0.15), 0, 255)
            img = Image.fromarray(arr.astype(np.uint8))

        v = adj.get("vibrance", 0)
        if v != 0:
            arr = np.array(img, dtype=np.uint8)
            hsv = cv2.cvtColor(arr, cv2.COLOR_RGB2HSV).astype(np.float32)
            factor = v / 100.0
            sat = hsv[:, :, 1] / 255.0
            boost = factor * 50 * (1.0 - sat)
            hsv[:, :, 1] = np.clip(hsv[:, :, 1] + boost, 0, 255)
            img = Image.fromarray(cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB))

        e = adj.get("exposure", 0)
        if e != 0:
            arr = np.array(img, dtype=np.float32)
            stops = e / 100.0
            arr = arr * (2 ** stops)
            img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))

        return img
