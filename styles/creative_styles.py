from PIL import Image
import numpy as np
from styles.base_style import BaseStyle


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

    def get_palette(self) -> dict:
        return self._palette

    def process_subject(self, image: Image.Image) -> Image.Image:
        arr = np.array(image.convert("RGB"), dtype=np.float32)
        r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
        nr = np.clip(r * 0.8 + g * 0.1 + b * 0.1 + 20, 0, 255)
        ng = np.clip(g * 0.4 + b * 0.6, 0, 255)
        nb = np.clip(b * 1.6, 0, 255)
        return Image.fromarray(np.stack([nr, ng, nb], axis=2).astype(np.uint8))


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

    def get_palette(self) -> dict:
        return self._palette

    def process_subject(self, image: Image.Image) -> Image.Image:
        arr = np.array(image.convert("RGB"), dtype=np.float32)
        gray = np.mean(arr, axis=2, keepdims=True)
        pink = np.clip(gray * 0.9 + 30, 0, 255)
        cyan = np.clip(gray * 0.7 + 40, 0, 255)
        blue = np.clip(gray * 1.1, 0, 255)
        r = np.clip(pink * 0.7 + arr[:, :, 0:1] * 0.3, 0, 255)
        g = np.clip(arr[:, :, 1:2] * 0.3 + gray * 0.3, 0, 255)
        b = np.clip(cyan * 0.4 + blue * 0.3 + arr[:, :, 2:3] * 0.3, 0, 255)
        return Image.fromarray(np.concatenate([r, g, b], axis=2).astype(np.uint8))


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
        self._neon_color = (255, 0, 200)
        self._intensity = 0.7

    def get_palette(self) -> dict:
        return self._palette

    def get_style_params(self) -> dict[str, dict]:
        return {
            "color": {"label": "Color neon", "type": "color", "value": self._neon_color},
            "intensity": {"label": "Intensidad", "type": "slider", "min": 0, "max": 100, "value": int(self._intensity * 100)},
        }

    def update_style_param(self, name: str, value):
        if name == "color":
            self._neon_color = value
        elif name == "intensity":
            self._intensity = value / 100.0

    def process_subject(self, image: Image.Image) -> Image.Image:
        arr = np.array(image.convert("RGB"), dtype=np.float32)
        gray = np.mean(arr, axis=2, keepdims=True) / 255.0
        nr, ng, nb = self._neon_color
        r = np.clip(gray * nr * self._intensity + arr[:, :, 0:1] * (1 - self._intensity), 0, 255)
        g = np.clip(gray * ng * self._intensity + arr[:, :, 1:2] * (1 - self._intensity), 0, 255)
        b = np.clip(gray * nb * self._intensity + arr[:, :, 2:3] * (1 - self._intensity), 0, 255)
        return Image.fromarray(np.concatenate([r, g, b], axis=2).astype(np.uint8))


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
