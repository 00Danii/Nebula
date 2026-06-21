from PIL import Image, ImageDraw
import numpy as np
import cv2
from styles.base_style import BaseStyle


def _glow_bloom(img_array: np.ndarray, threshold_pct: float,
                color: tuple[int, int, int], intensity: float,
                radius_pct: float = 0.04) -> np.ndarray:
    gray = np.mean(img_array, axis=2)
    thresh = np.percentile(gray, threshold_pct)
    mask = gray > thresh
    if not np.any(mask):
        return img_array
    bloom = img_array.copy()
    bloom[~np.stack([mask] * 3, axis=2)] = 0
    ksize = max(3, int(min(img_array.shape[:2]) * radius_pct) | 1)
    bloom = cv2.GaussianBlur(bloom, (ksize, ksize), ksize * 0.3)
    cr, cg, cb = color
    bloom[:, :, 0] *= cr / 255.0
    bloom[:, :, 1] *= cg / 255.0
    bloom[:, :, 2] *= cb / 255.0
    return np.clip(img_array + bloom * intensity, 0, 255)


class TritoneStyle(BaseStyle):
    @property
    def id(self) -> str:
        return "tritone"

    @property
    def name(self) -> str:
        return "Tritono"

    def __init__(self):
        super().__init__()
        self._background_color = (0, 0, 0)
        self._palette = {
            "text": (255, 220, 180),
            "grid": (120, 60, 180),
            "accent": (60, 30, 120),
        }
        self._shadow_color = (20, 10, 50)
        self._midtone_color = (120, 60, 180)
        self._highlight_color = (255, 220, 180)
        self._balance: int = 50
        self._blend: int = 100

    def get_palette(self) -> dict:
        return self._palette

    def get_style_params(self) -> dict[str, dict]:
        return {
            "shadow": {"label": "Sombra", "type": "color", "value": self._shadow_color},
            "midtone": {"label": "Medio", "type": "color", "value": self._midtone_color},
            "highlight": {"label": "Luz", "type": "color", "value": self._highlight_color},
            "balance": {"label": "Balance", "type": "slider", "min": 0, "max": 100, "value": self._balance},
            "blend": {"label": "Mezcla", "type": "slider", "min": 0, "max": 100, "value": self._blend},
        }

    def get_style_param_groups(self) -> list[dict]:
        return [
            {
                "title": "Colores",
                "params": {
                    "shadow": {"label": "Sombra", "type": "color", "value": self._shadow_color},
                    "midtone": {"label": "Medio", "type": "color", "value": self._midtone_color},
                    "highlight": {"label": "Luz", "type": "color", "value": self._highlight_color},
                },
            },
            {
                "title": "Ajustes",
                "params": {
                    "balance": {"label": "Balance", "type": "slider", "min": 0, "max": 100, "value": self._balance},
                    "blend": {"label": "Mezcla", "type": "slider", "min": 0, "max": 100, "value": self._blend},
                },
            },
        ]

    def update_style_param(self, name: str, value):
        if name == "shadow":
            self._shadow_color = value
        elif name == "midtone":
            self._midtone_color = value
        elif name == "highlight":
            self._highlight_color = value
        elif name == "balance":
            self._balance = int(value)
        elif name == "blend":
            self._blend = int(value)

    def process_subject(self, image: Image.Image) -> Image.Image:
        gray = np.array(image.convert("L"), dtype=np.float32) / 255.0
        original = gray.copy()
        sr, sg, sb = self._shadow_color
        mr, mg, mb = self._midtone_color
        hr, hg, hb = self._highlight_color

        mid = max(0.05, min(0.95, self._balance / 100.0))
        mask_shadow = gray <= mid
        t1 = gray / mid
        t2 = (gray - mid) / (1.0 - mid)

        r = np.where(mask_shadow, (1 - t1) * sr + t1 * mr, (1 - t2) * mr + t2 * hr)
        g = np.where(mask_shadow, (1 - t1) * sg + t1 * mg, (1 - t2) * mg + t2 * hg)
        b = np.where(mask_shadow, (1 - t1) * sb + t1 * mb, (1 - t2) * mb + t2 * hb)

        result = np.stack([r, g, b], axis=2)

        blend = self._blend / 100.0
        if blend < 1.0:
            gray3 = np.stack([original * 255] * 3, axis=2)
            result = result * blend + gray3 * (1.0 - blend)

        return Image.fromarray(np.clip(result, 0, 255).astype(np.uint8))


class CyberpunkStyle(BaseStyle):
    @property
    def id(self) -> str:
        return "cyberpunk"

    @property
    def name(self) -> str:
        return "Cyberpunk Neon"

    def __init__(self):
        super().__init__()
        self._background_color = (0, 0, 0)
        self._palette = {
            "text": (255, 0, 128),
            "grid": (80, 0, 40),
            "accent": (0, 255, 255),
        }
        self._glow_color: tuple[int, int, int] = (255, 0, 128)
        self._glow_intensity: int = 40
        self._glow_threshold: int = 30
        self._scanlines: int = 0
        self._vignette: int = 40

    def get_palette(self) -> dict:
        return self._palette

    def get_style_params(self) -> dict[str, dict]:
        return {
            "glow_color": {"label": "Brillo neon", "type": "color", "value": self._glow_color},
            "glow_intensity": {"label": "Intensidad brillo", "type": "slider", "min": 0, "max": 100, "value": self._glow_intensity},
            "glow_threshold": {"label": "Umbral brillo", "type": "slider", "min": 0, "max": 100, "value": self._glow_threshold},
            "scanlines": {"label": "Lineas digitales", "type": "slider", "min": 0, "max": 100, "value": self._scanlines},
            "vignette": {"label": "Vi\u00f1eta", "type": "slider", "min": 0, "max": 100, "value": self._vignette},
        }

    def get_style_param_groups(self) -> list[dict]:
        return [
            {
                "title": "Neon",
                "params": {
                    "glow_color": {"label": "Brillo neon", "type": "color", "value": self._glow_color},
                    "glow_intensity": {"label": "Intensidad brillo", "type": "slider", "min": 0, "max": 100, "value": self._glow_intensity},
                    "glow_threshold": {"label": "Umbral brillo", "type": "slider", "min": 0, "max": 100, "value": self._glow_threshold},
                },
            },
            {
                "title": "Overlay",
                "params": {
                    "scanlines": {"label": "Lineas digitales", "type": "slider", "min": 0, "max": 100, "value": self._scanlines},
                    "vignette": {"label": "Vi\u00f1eta", "type": "slider", "min": 0, "max": 100, "value": self._vignette},
                },
            },
        ]

    def update_style_param(self, name: str, value):
        if name == "glow_color":
            self._glow_color = value
        elif name == "glow_intensity":
            self._glow_intensity = int(value)
        elif name == "glow_threshold":
            self._glow_threshold = int(value)
        elif name == "scanlines":
            self._scanlines = int(value)
        elif name == "vignette":
            self._vignette = int(value)

    def process_subject(self, image: Image.Image) -> Image.Image:
        arr = np.array(image.convert("RGB"), dtype=np.float32)
        r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
        nr = np.clip(r * 0.8 + g * 0.1 + b * 0.1 + 20, 0, 255)
        ng = np.clip(g * 0.4 + b * 0.6, 0, 255)
        nb = np.clip(b * 1.6, 0, 255)
        result = np.stack([nr, ng, nb], axis=2)

        if self._glow_intensity > 0:
            result = _glow_bloom(
                result,
                max(5, 100 - self._glow_threshold),
                self._glow_color,
                self._glow_intensity / 100.0 * 0.5,
                0.035,
            )

        return Image.fromarray(np.clip(result, 0, 255).astype(np.uint8))

    def apply_post_effects(self, canvas: Image.Image, draw: ImageDraw.ImageDraw, size: tuple[int, int]):
        w, h = size
        img = np.array(canvas, dtype=np.float32)

        if self._scanlines > 0:
            mask = np.ones((h, w, 3), dtype=np.float32)
            intensity = self._scanlines / 100.0 * 0.3
            for y in range(0, h, 4):
                mask[y, :, :] = 1.0 - intensity
            img *= mask

        if self._vignette > 0:
            strength = self._vignette / 100.0
            x = np.arange(w, dtype=np.float32)
            y = np.arange(h, dtype=np.float32)
            mx, my = np.meshgrid(x, y)
            nx = (mx - w / 2.0) / (w / 2.0)
            ny = (my - h / 2.0) / (h / 2.0)
            d = np.sqrt(nx * nx + ny * ny)
            v = np.clip(1.0 - d * strength * 0.7, 0, 1)
            img *= v[:, :, np.newaxis]

        canvas.paste(Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)))


class VaporwaveStyle(BaseStyle):
    @property
    def id(self) -> str:
        return "vaporwave"

    @property
    def name(self) -> str:
        return "Vaporwave Retro"

    def __init__(self):
        super().__init__()
        self._background_color = (0, 0, 0)
        self._palette = {
            "text": (255, 100, 200),
            "grid": (60, 0, 40),
            "accent": (0, 200, 255),
        }
        self._glow_color: tuple[int, int, int] = (255, 100, 200)
        self._glow_intensity: int = 50
        self._pink_strength: int = 70
        self._cyan_strength: int = 40
        self._fade: int = 0
        self._vignette: int = 30

    def get_palette(self) -> dict:
        return self._palette

    def get_style_params(self) -> dict[str, dict]:
        return {
            "glow_color": {"label": "Resplandor", "type": "color", "value": self._glow_color},
            "glow_intensity": {"label": "Intensidad resplandor", "type": "slider", "min": 0, "max": 100, "value": self._glow_intensity},
            "pink_strength": {"label": "Rosa", "type": "slider", "min": 0, "max": 100, "value": self._pink_strength},
            "cyan_strength": {"label": "Cian", "type": "slider", "min": 0, "max": 100, "value": self._cyan_strength},
            "fade": {"label": "Desvanecer", "type": "slider", "min": 0, "max": 100, "value": self._fade},
            "vignette": {"label": "Vi\u00f1eta", "type": "slider", "min": 0, "max": 100, "value": self._vignette},
        }

    def get_style_param_groups(self) -> list[dict]:
        return [
            {
                "title": "Resplandor",
                "params": {
                    "glow_color": {"label": "Resplandor", "type": "color", "value": self._glow_color},
                    "glow_intensity": {"label": "Intensidad resplandor", "type": "slider", "min": 0, "max": 100, "value": self._glow_intensity},
                },
            },
            {
                "title": "Color",
                "params": {
                    "pink_strength": {"label": "Rosa", "type": "slider", "min": 0, "max": 100, "value": self._pink_strength},
                    "cyan_strength": {"label": "Cian", "type": "slider", "min": 0, "max": 100, "value": self._cyan_strength},
                },
            },
            {
                "title": "Efectos",
                "params": {
                    "fade": {"label": "Desvanecer", "type": "slider", "min": 0, "max": 100, "value": self._fade},
                    "vignette": {"label": "Vi\u00f1eta", "type": "slider", "min": 0, "max": 100, "value": self._vignette},
                },
            },
        ]

    def update_style_param(self, name: str, value):
        if name == "glow_color":
            self._glow_color = value
        elif name == "glow_intensity":
            self._glow_intensity = int(value)
        elif name == "pink_strength":
            self._pink_strength = int(value)
        elif name == "cyan_strength":
            self._cyan_strength = int(value)
        elif name == "fade":
            self._fade = int(value)
        elif name == "vignette":
            self._vignette = int(value)

    def process_subject(self, image: Image.Image) -> Image.Image:
        arr = np.array(image.convert("RGB"), dtype=np.float32)
        gray = np.mean(arr, axis=2, keepdims=True)
        pink_factor = self._pink_strength / 100.0
        cyan_factor = self._cyan_strength / 100.0
        pink = np.clip(gray * 0.9 + 30, 0, 255)
        cyan = np.clip(gray * 0.7 + 40, 0, 255)
        blue = np.clip(gray * 1.1, 0, 255)
        r = np.clip(pink * pink_factor + arr[:, :, 0:1] * (1.0 - pink_factor * 0.7), 0, 255)
        g = np.clip(arr[:, :, 1:2] * 0.3 + gray * 0.3, 0, 255)
        b = np.clip(cyan * cyan_factor + blue * 0.3 + arr[:, :, 2:3] * 0.3, 0, 255)
        result = np.concatenate([r, g, b], axis=2)

        if self._glow_intensity > 0:
            result = _glow_bloom(
                result, 70, self._glow_color,
                self._glow_intensity / 100.0 * 0.4, 0.05,
            )

        fade = self._fade / 100.0
        if fade > 0:
            gray_fade = np.mean(result, axis=2, keepdims=True)
            result = result * (1.0 - fade * 0.5) + gray_fade * (fade * 0.5)
            result = np.clip(result + 15 * fade, 0, 255)

        if self._vignette > 0:
            h, w = result.shape[:2]
            strength = self._vignette / 100.0
            x = np.arange(w, dtype=np.float32)
            y = np.arange(h, dtype=np.float32)
            mx, my = np.meshgrid(x, y)
            nx = (mx - w / 2.0) / (w / 2.0)
            ny = (my - h / 2.0) / (h / 2.0)
            d = np.sqrt(nx * nx + ny * ny)
            v = np.clip(1.0 - d * strength * 0.7, 0, 1)
            result *= v[:, :, np.newaxis]

        return Image.fromarray(np.clip(result, 0, 255).astype(np.uint8))


class GoldStyle(BaseStyle):
    @property
    def id(self) -> str:
        return "gold"

    @property
    def name(self) -> str:
        return "Dorado Metalico"

    def __init__(self):
        super().__init__()
        self._background_color = (0, 0, 0)
        self._palette = {
            "text": (255, 215, 0),
            "grid": (80, 60, 0),
            "accent": (255, 180, 50),
        }

    def get_palette(self) -> dict:
        return self._palette

    def process_subject(self, image: Image.Image) -> Image.Image:
        arr = np.array(image.convert("RGB"), dtype=np.float32)
        gray = np.mean(arr, axis=2, keepdims=True)
        gold_r = np.clip(gray * 1.1 + 20, 0, 255)
        gold_g = np.clip(gray * 0.85 + 10, 0, 255)
        gold_b = np.clip(gray * 0.4, 0, 255)
        return Image.fromarray(np.concatenate([gold_r, gold_g, gold_b], axis=2).astype(np.uint8))


class IceStyle(BaseStyle):
    @property
    def id(self) -> str:
        return "ice"

    @property
    def name(self) -> str:
        return "Hielo Azul"

    def __init__(self):
        super().__init__()
        self._background_color = (0, 0, 0)
        self._palette = {
            "text": (180, 230, 255),
            "grid": (40, 80, 100),
            "accent": (100, 200, 255),
        }

    def get_palette(self) -> dict:
        return self._palette

    def process_subject(self, image: Image.Image) -> Image.Image:
        arr = np.array(image.convert("RGB"), dtype=np.float32)
        gray = np.mean(arr, axis=2, keepdims=True)
        r = np.clip(gray * 0.7 - 10, 0, 255)
        g = np.clip(gray * 0.9 + 10, 0, 255)
        b = np.clip(gray * 1.2 + 20, 0, 255)
        return Image.fromarray(np.concatenate([r, g, b], axis=2).astype(np.uint8))


class PastelStyle(BaseStyle):
    @property
    def id(self) -> str:
        return "pastel"

    @property
    def name(self) -> str:
        return "Pastel Suave"

    def __init__(self):
        super().__init__()
        self._background_color = (0, 0, 0)
        self._palette = {
            "text": (220, 200, 210),
            "grid": (80, 70, 75),
            "accent": (200, 180, 190),
        }

    def get_palette(self) -> dict:
        return self._palette

    def process_subject(self, image: Image.Image) -> Image.Image:
        arr = np.array(image.convert("RGB"), dtype=np.float32)
        gray = np.mean(arr, axis=2, keepdims=True)
        blend = 0.6
        pastel_r = np.clip(gray * 0.9 + 20, 0, 255)
        pastel_g = np.clip(gray * 0.85 + 25, 0, 255)
        pastel_b = np.clip(gray * 0.95 + 15, 0, 255)
        r = np.clip(arr[:, :, 0:1] * (1 - blend) + pastel_r * blend, 0, 255)
        g = np.clip(arr[:, :, 1:2] * (1 - blend) + pastel_g * blend, 0, 255)
        b = np.clip(arr[:, :, 2:3] * (1 - blend) + pastel_b * blend, 0, 255)
        return Image.fromarray(np.concatenate([r, g, b], axis=2).astype(np.uint8))


class MutedStyle(BaseStyle):
    @property
    def id(self) -> str:
        return "muted"

    @property
    def name(self) -> str:
        return "Fotografia Mate"

    def __init__(self):
        super().__init__()
        self._background_color = (0, 0, 0)
        self._palette = {
            "text": (160, 150, 140),
            "grid": (60, 55, 50),
            "accent": (130, 120, 110),
        }
        self._fade = 0.5

    def get_palette(self) -> dict:
        return self._palette

    def get_style_params(self) -> dict[str, dict]:
        return {
            "fade": {"label": "Desvanecer", "type": "slider", "min": 0, "max": 100, "value": int(self._fade * 100)},
        }

    def update_style_param(self, name: str, value):
        if name == "fade":
            self._fade = value / 100.0

    def process_subject(self, image: Image.Image) -> Image.Image:
        arr = np.array(image.convert("RGB"), dtype=np.float32)
        gray = np.mean(arr, axis=2, keepdims=True)
        faded = arr * (1 - self._fade * 0.6) + gray * (self._fade * 0.6)
        faded = np.clip(faded + 20 * self._fade, 0, 255)
        return Image.fromarray(faded.astype(np.uint8))


class InvertStyle(BaseStyle):
    @property
    def id(self) -> str:
        return "invert"

    @property
    def name(self) -> str:
        return "Negativo"

    def __init__(self):
        super().__init__()
        self._background_color = (0, 0, 0)
        self._palette = {
            "text": (0, 255, 255),
            "grid": (100, 100, 100),
            "accent": (255, 100, 100),
        }
        self._mode: str = "completo"
        self._threshold: int = 50
        self._blend: int = 100
        self._tint_color: tuple[int, int, int] = (255, 255, 255)

    def get_palette(self) -> dict:
        return self._palette

    def get_style_params(self) -> dict[str, dict]:
        return {
            "mode": {"label": "Modo", "type": "choice", "options": ["completo", "luminancia", "selectivo", "solarizado"], "value": self._mode},
            "threshold": {"label": "Umbral", "type": "slider", "min": 0, "max": 100, "value": self._threshold},
            "blend": {"label": "Mezcla", "type": "slider", "min": 0, "max": 100, "value": self._blend},
            "tint": {"label": "Tinte", "type": "color", "value": self._tint_color},
        }

    def get_style_param_groups(self) -> list[dict]:
        return [
            {
                "title": "Modo",
                "params": {
                    "mode": {"label": "Modo", "type": "choice", "options": ["completo", "luminancia", "selectivo", "solarizado"], "value": self._mode},
                    "threshold": {"label": "Umbral", "type": "slider", "min": 0, "max": 100, "value": self._threshold},
                },
            },
            {
                "title": "Ajustes",
                "params": {
                    "blend": {"label": "Mezcla", "type": "slider", "min": 0, "max": 100, "value": self._blend},
                    "tint": {"label": "Tinte", "type": "color", "value": self._tint_color},
                },
            },
        ]

    def update_style_param(self, name: str, value):
        if name == "mode":
            self._mode = value
        elif name == "threshold":
            self._threshold = int(value)
        elif name == "blend":
            self._blend = int(value)
        elif name == "tint":
            self._tint_color = value

    def process_subject(self, image: Image.Image) -> Image.Image:
        arr = np.array(image.convert("RGB"), dtype=np.float32)

        if self._mode == "completo":
            result = 255.0 - arr
        elif self._mode == "luminancia":
            gray = np.mean(arr, axis=2, keepdims=True)
            inv_gray = 255.0 - gray
            result = arr * 0.3 + inv_gray * 0.7
        elif self._mode == "selectivo":
            gray = np.mean(arr, axis=2)
            t = self._threshold / 100.0 * 255.0
            mask = gray > t
            result = arr.copy()
            for c in range(3):
                channel = result[:, :, c]
                channel[mask] = 255.0 - channel[mask]
        else:
            t = self._threshold / 100.0
            gray = np.mean(arr, axis=2, keepdims=True) / 255.0
            invert_amount = 1.0 - np.abs(gray - t) * 2.0
            invert_amount = np.clip(invert_amount, 0, 1)
            result = arr * (1.0 - invert_amount) + (255.0 - arr) * invert_amount

        blend = self._blend / 100.0
        if blend < 1.0:
            result = result * blend + arr * (1.0 - blend)

        tr, tg, tb = self._tint_color
        if (tr, tg, tb) != (255, 255, 255):
            gray_res = np.mean(result, axis=2, keepdims=True) / 255.0
            result = np.concatenate([
                gray_res * tr,
                gray_res * tg,
                gray_res * tb,
            ], axis=2)

        return Image.fromarray(np.clip(result, 0, 255).astype(np.uint8))


class NeonStyle(BaseStyle):
    @property
    def id(self) -> str:
        return "neon"

    @property
    def name(self) -> str:
        return "Neon Brillante"

    def __init__(self):
        super().__init__()
        self._background_color = (0, 0, 0)
        self._palette = {
            "text": (255, 50, 200),
            "grid": (50, 0, 40),
            "accent": (50, 255, 200),
        }
        self._neon_color1: tuple[int, int, int] = (255, 0, 200)
        self._neon_color2: tuple[int, int, int] = (0, 200, 255)
        self._intensity: int = 70
        self._glow_intensity: int = 50
        self._glow_radius: int = 50
        self._glow_threshold: int = 30

    def get_palette(self) -> dict:
        return self._palette

    def get_style_params(self) -> dict[str, dict]:
        return {
            "color1": {"label": "Color 1", "type": "color", "value": self._neon_color1},
            "color2": {"label": "Color 2", "type": "color", "value": self._neon_color2},
            "intensity": {"label": "Intensidad", "type": "slider", "min": 0, "max": 100, "value": self._intensity},
            "glow_intensity": {"label": "Brillo", "type": "slider", "min": 0, "max": 100, "value": self._glow_intensity},
            "glow_radius": {"label": "Radio brillo", "type": "slider", "min": 0, "max": 100, "value": self._glow_radius},
            "glow_threshold": {"label": "Umbral brillo", "type": "slider", "min": 0, "max": 100, "value": self._glow_threshold},
        }

    def get_style_param_groups(self) -> list[dict]:
        return [
            {
                "title": "Colores neon",
                "params": {
                    "color1": {"label": "Color 1", "type": "color", "value": self._neon_color1},
                    "color2": {"label": "Color 2", "type": "color", "value": self._neon_color2},
                    "intensity": {"label": "Intensidad", "type": "slider", "min": 0, "max": 100, "value": self._intensity},
                },
            },
            {
                "title": "Brillo",
                "params": {
                    "glow_intensity": {"label": "Brillo", "type": "slider", "min": 0, "max": 100, "value": self._glow_intensity},
                    "glow_radius": {"label": "Radio brillo", "type": "slider", "min": 0, "max": 100, "value": self._glow_radius},
                    "glow_threshold": {"label": "Umbral brillo", "type": "slider", "min": 0, "max": 100, "value": self._glow_threshold},
                },
            },
        ]

    def update_style_param(self, name: str, value):
        if name == "color1":
            self._neon_color1 = value
        elif name == "color2":
            self._neon_color2 = value
        elif name == "intensity":
            self._intensity = int(value)
        elif name == "glow_intensity":
            self._glow_intensity = int(value)
        elif name == "glow_radius":
            self._glow_radius = int(value)
        elif name == "glow_threshold":
            self._glow_threshold = int(value)

    def process_subject(self, image: Image.Image) -> Image.Image:
        arr = np.array(image.convert("RGB"), dtype=np.float32)
        gray = np.mean(arr, axis=2, keepdims=True) / 255.0
        intensity = self._intensity / 100.0

        n1r, n1g, n1b = self._neon_color1
        n2r, n2g, n2b = self._neon_color2

        blend = gray
        r = np.clip(blend * (n1r * (1.0 - gray) + n2r * gray) * intensity +
                    arr[:, :, 0:1] * (1.0 - intensity), 0, 255)
        g = np.clip(blend * (n1g * (1.0 - gray) + n2g * gray) * intensity +
                    arr[:, :, 1:2] * (1.0 - intensity), 0, 255)
        b = np.clip(blend * (n1b * (1.0 - gray) + n2b * gray) * intensity +
                    arr[:, :, 2:3] * (1.0 - intensity), 0, 255)
        result = np.concatenate([r, g, b], axis=2)

        if self._glow_intensity > 0:
            radius_pct = 0.02 + (self._glow_radius / 100.0) * 0.08
            result = _glow_bloom(
                result,
                max(5, 100 - self._glow_threshold),
                self._neon_color1,
                self._glow_intensity / 100.0 * 0.6,
                radius_pct,
            )

        return Image.fromarray(np.clip(result, 0, 255).astype(np.uint8))


class DuotoneStyle(BaseStyle):
    @property
    def id(self) -> str:
        return "duotone"

    @property
    def name(self) -> str:
        return "Duotono"

    def __init__(self):
        super().__init__()
        self._background_color = (0, 0, 0)
        self._palette = {
            "text": (255, 200, 100),
            "grid": (60, 40, 20),
            "accent": (200, 100, 255),
        }
        self._shadow_color = (20, 10, 50)
        self._highlight_color = (255, 200, 100)
        self._balance: int = 50
        self._blend: int = 100

    def get_palette(self) -> dict:
        return self._palette

    def get_style_params(self) -> dict[str, dict]:
        return {
            "shadow": {"label": "Sombra", "type": "color", "value": self._shadow_color},
            "highlight": {"label": "Luz", "type": "color", "value": self._highlight_color},
            "balance": {"label": "Balance", "type": "slider", "min": 0, "max": 100, "value": self._balance},
            "blend": {"label": "Mezcla", "type": "slider", "min": 0, "max": 100, "value": self._blend},
        }

    def get_style_param_groups(self) -> list[dict]:
        return [
            {
                "title": "Colores",
                "params": {
                    "shadow": {"label": "Sombra", "type": "color", "value": self._shadow_color},
                    "highlight": {"label": "Luz", "type": "color", "value": self._highlight_color},
                },
            },
            {
                "title": "Ajustes",
                "params": {
                    "balance": {"label": "Balance", "type": "slider", "min": 0, "max": 100, "value": self._balance},
                    "blend": {"label": "Mezcla", "type": "slider", "min": 0, "max": 100, "value": self._blend},
                },
            },
        ]

    def update_style_param(self, name: str, value):
        if name == "shadow":
            self._shadow_color = value
        elif name == "highlight":
            self._highlight_color = value
        elif name == "balance":
            self._balance = int(value)
        elif name == "blend":
            self._blend = int(value)

    def process_subject(self, image: Image.Image) -> Image.Image:
        gray = np.array(image.convert("L"), dtype=np.float32) / 255.0
        original = gray.copy()
        sr, sg, sb = self._shadow_color
        hr, hg, hb = self._highlight_color

        exp = max(0.1, (100 - self._balance) / 50.0)
        mapped = np.power(np.clip(gray, 0.001, 1.0), exp)

        r = (1 - mapped) * sr + mapped * hr
        g = (1 - mapped) * sg + mapped * hg
        b = (1 - mapped) * sb + mapped * hb

        result = np.stack([r, g, b], axis=2)

        blend = self._blend / 100.0
        if blend < 1.0:
            gray3 = np.stack([original * 255] * 3, axis=2)
            result = result * blend + gray3 * (1.0 - blend)

        return Image.fromarray(np.clip(result, 0, 255).astype(np.uint8))
