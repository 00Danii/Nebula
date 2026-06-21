from PIL import Image
import numpy as np
from styles.base_style import BaseStyle


def _param(label, ptype, default, **kw):
    p = {"label": label, "type": ptype, "value": default}
    p.update(kw)
    return p


class CustomStyle(BaseStyle):
    @property
    def id(self) -> str:
        return "custom"

    @property
    def name(self) -> str:
        return "Personalizado"

    def __init__(self):
        super().__init__()
        self._background_color = (0, 0, 0)
        self._palette = {
            "text": (200, 200, 200),
            "grid": (80, 80, 80),
            "accent": (150, 150, 150),
        }
        self._p: dict[str, float | tuple] = {}

        for group in self._param_groups():
            for k, v in group["params"].items():
                self._p[k] = v["value"]

    def get_palette(self) -> dict:
        return self._palette

    def _param_groups(self) -> list[dict]:
        return [
            {
                "title": "Niveles RGB",
                "params": {
                    "level_r_black": _param("Negro R", "slider", 0, min=0, max=100),
                    "level_r_gamma": _param("Gamma R", "slider", 100, min=20, max=300),
                    "level_r_white": _param("Blanco R", "slider", 255, min=155, max=255),
                    "level_g_black": _param("Negro G", "slider", 0, min=0, max=100),
                    "level_g_gamma": _param("Gamma G", "slider", 100, min=20, max=300),
                    "level_g_white": _param("Blanco G", "slider", 255, min=155, max=255),
                    "level_b_black": _param("Negro B", "slider", 0, min=0, max=100),
                    "level_b_gamma": _param("Gamma B", "slider", 100, min=20, max=300),
                    "level_b_white": _param("Blanco B", "slider", 255, min=155, max=255),
                },
            },
            {
                "title": "Balance de Color - Sombras",
                "params": {
                    "cb_shadow_r": _param("Rojo", "slider", 0, min=-100, max=100),
                    "cb_shadow_g": _param("Verde", "slider", 0, min=-100, max=100),
                    "cb_shadow_b": _param("Azul", "slider", 0, min=-100, max=100),
                },
            },
            {
                "title": "Balance de Color - Medios",
                "params": {
                    "cb_midtone_r": _param("Rojo", "slider", 0, min=-100, max=100),
                    "cb_midtone_g": _param("Verde", "slider", 0, min=-100, max=100),
                    "cb_midtone_b": _param("Azul", "slider", 0, min=-100, max=100),
                },
            },
            {
                "title": "Balance de Color - Luces",
                "params": {
                    "cb_highlight_r": _param("Rojo", "slider", 0, min=-100, max=100),
                    "cb_highlight_g": _param("Verde", "slider", 0, min=-100, max=100),
                    "cb_highlight_b": _param("Azul", "slider", 0, min=-100, max=100),
                },
            },
            {
                "title": "Tono Dividido",
                "params": {
                    "st_shadow": _param("Color sombra", "color", (30, 10, 60)),
                    "st_highlight": _param("Color luz", "color", (255, 220, 180)),
                    "st_balance": _param("Balance", "slider", 0, min=-100, max=100),
                },
            },
            {
                "title": "HSL Global",
                "params": {
                    "hsl_hue": _param("Tono", "slider", 0, min=-180, max=180),
                    "hsl_sat": _param("Saturacion", "slider", 0, min=-100, max=100),
                    "hsl_light": _param("Luminosidad", "slider", 0, min=-100, max=100),
                },
            },
            {
                "title": "Globales",
                "params": {
                    "temperature": _param("Temperatura", "slider", 0, min=-100, max=100),
                    "tint": _param("Tinte", "slider", 0, min=-100, max=100),
                    "vibrance": _param("Vibrancia", "slider", 0, min=-100, max=100),
                    "saturation": _param("Saturacion global", "slider", 0, min=-100, max=100),
                },
            },
        ]

    def get_style_params(self) -> dict[str, dict]:
        flat = {}
        for group in self._param_groups():
            for k, v in group["params"].items():
                flat[k] = v
        return flat

    def get_style_param_groups(self) -> list[dict]:
        return self._param_groups()

    def update_style_param(self, name: str, value):
        self._p[name] = value

    def process_subject(self, image: Image.Image) -> Image.Image:
        arr = np.array(image.convert("RGB"), dtype=np.float32)

        arr = self._apply_levels(arr)
        arr = self._apply_split_tone(arr)
        arr = self._apply_hsl_global(arr)
        arr = self._apply_globals(arr)

        return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))

    def _apply_levels(self, arr: np.ndarray) -> np.ndarray:
        for i, ch in enumerate(["r", "g", "b"]):
            c = arr[:, :, i].copy()
            black = self._p.get(f"level_{ch}_black", 0)
            white = self._p.get(f"level_{ch}_white", 255)
            gamma = self._p.get(f"level_{ch}_gamma", 100) / 100.0
            c = np.clip((c - black) / max(white - black, 1) * 255, 0, 255)
            c = np.power(np.clip(c / 255.0, 0.001, 1.0), 1.0 / gamma) * 255
            arr[:, :, i] = c
        return arr

    def _apply_split_tone(self, arr: np.ndarray) -> np.ndarray:
        sh = self._p.get("st_shadow", (30, 10, 60))
        hl = self._p.get("st_highlight", (255, 220, 180))
        bal = self._p.get("st_balance", 0) / 100.0

        gray = np.mean(arr, axis=2)
        norm = gray / 255.0
        shadow_weight = np.clip(1.0 - norm * (1 + bal), 0, 1)
        highlight_weight = np.clip(norm * (1 - bal), 0, 1)

        for i in range(3):
            arr[:, :, i] += shadow_weight * (sh[i] - 128) * 0.3
            arr[:, :, i] += highlight_weight * (hl[i] - 128) * 0.3

        return arr

    def _apply_hsl_global(self, arr: np.ndarray) -> np.ndarray:
        h_shift = self._p.get("hsl_hue", 0)
        s_adj = self._p.get("hsl_sat", 0)
        l_adj = self._p.get("hsl_light", 0)

        if h_shift == 0 and s_adj == 0 and l_adj == 0:
            return arr

        import cv2
        hsv = cv2.cvtColor(arr, cv2.COLOR_RGB2HSV).astype(np.float32)
        hsv[:, :, 0] = (hsv[:, :, 0] + h_shift) % 180
        hsv[:, :, 1] = np.clip(hsv[:, :, 1] * (1 + s_adj / 100.0), 0, 255)
        hsv[:, :, 2] = np.clip(hsv[:, :, 2] * (1 + l_adj / 100.0), 0, 255)
        return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB).astype(np.float32)

    def _apply_globals(self, arr: np.ndarray) -> np.ndarray:
        temp = self._p.get("temperature", 0)
        tint = self._p.get("tint", 0)
        vibrance = self._p.get("vibrance", 0)
        sat = self._p.get("saturation", 0)

        if temp != 0:
            arr[:, :, 0] *= 1 + temp / 300.0
            arr[:, :, 2] *= 1 - temp / 300.0

        if tint != 0:
            arr[:, :, 1] *= 1 + tint / 300.0

        if vibrance != 0:
            import cv2
            hsv = cv2.cvtColor(arr, cv2.COLOR_RGB2HSV).astype(np.float32)
            low_sat = 1.0 - hsv[:, :, 1] / 255.0
            boost = (vibrance / 100.0) * low_sat * 0.5
            hsv[:, :, 1] = np.clip(hsv[:, :, 1] * (1 + boost), 0, 255)
            arr = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB).astype(np.float32)

        if sat != 0:
            import cv2
            hsv = cv2.cvtColor(arr, cv2.COLOR_RGB2HSV).astype(np.float32)
            hsv[:, :, 1] = np.clip(hsv[:, :, 1] * (1 + sat / 100.0), 0, 255)
            arr = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB).astype(np.float32)

        return arr
