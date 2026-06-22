import math
import hashlib


class DataGenerator:
    def __init__(self):
        pass

    def _make_seed(self, *args) -> int:
        h = hashlib.md5(str(args).encode()).hexdigest()
        return int(h[:8], 16)

    def _map(self, val, in_lo, in_hi, out_lo, out_hi):
        t = (val - in_lo) / (in_hi - in_lo)
        return out_lo + t * (out_hi - out_lo)

    def generate_pole_coordinates(self, w, h, seed) -> str:
        r = self._make_seed(seed, "pole", w, h)
        ra_h = r % 24
        ra_m = (r >> 8) % 60
        dec_d = (r >> 16) % 180 - 90
        dec_m = (r >> 24) % 60
        return f"RA={ra_h:02d}h {ra_m:02d}m, Dec={dec_d:02d}\xb0 {dec_m:02d}'"

    def generate_sep_values(self, mean_r, mean_g, mean_b, seed) -> str:
        r = self._make_seed(seed, "sep", mean_r, mean_g, mean_b)
        w = self._map((r & 0xFF) / 255.0, 0, 1, 0, 360)
        delta = self._map(((r >> 8) & 0xFF) / 255.0, 0, 1, -20, 20)
        return f"w={w:.1f}\xb0, \u03b4={delta:.1f}\xb0"

    def generate_ssp_values(self, mean_l, std_l, seed) -> str:
        r = self._make_seed(seed, "ssp", mean_l, std_l)
        lam = self._map((r & 0xFF) / 255.0, 0, 1, -180, 180)
        beta = self._map(((r >> 8) & 0xFF) / 255.0, 0, 1, -90, 90)
        return f"\u03bb={lam:.1f}\xb0, \u00df={beta:.1f}\xb0"

    def generate_np_value(self, contrast, sharpness, seed) -> str:
        r = self._make_seed(seed, "np", contrast, sharpness)
        v = self._map((r & 0xFF) / 255.0, 0, 1, 0.5, 1.0)
        return f"{v:.2f}"

    def generate_arcseconds(self, w, h, zoom, seed) -> str:
        r = self._make_seed(seed, "arc", w, h, zoom)
        v = self._map((r & 0xFF) / 255.0, 0, 1, 0.1, 1.0)
        return f"{v:.2f}\""

    def generate_all(self, img_w, img_h, mean_rgb, mean_l, std_l, adjustments, style_id) -> dict[str, str]:
        seed = self._make_seed(img_w, img_h, style_id)
        mean_r, mean_g, mean_b = mean_rgb
        contrast = adjustments.get("contrast", 0)
        sharpness = adjustments.get("sharpness", 0)
        zoom = 1.0
        return {
            "pole": self.generate_pole_coordinates(img_w, img_h, seed),
            "sep": self.generate_sep_values(mean_r, mean_g, mean_b, seed),
            "ssp": self.generate_ssp_values(mean_l, std_l, seed),
            "np": self.generate_np_value(contrast, sharpness, seed),
            "arc": self.generate_arcseconds(img_w, img_h, zoom, seed),
        }
