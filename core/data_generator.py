import random
import math


class DataGenerator:
    def __init__(self, seed: int | None = None):
        self._rng = random.Random(seed)

    def generate_pole_coordinates(self) -> str:
        ra_h = self._rng.randint(0, 23)
        ra_m = self._rng.randint(0, 59)
        dec_d = self._rng.randint(-90, 89)
        dec_m = self._rng.randint(0, 59)
        return f"RA={ra_h:02d}h {ra_m:02d}m, Dec={dec_d:02d}\xb0 {dec_m:02d}'"

    def generate_sep_values(self) -> str:
        w = self._rng.uniform(0, 360)
        delta = self._rng.uniform(-20, 20)
        return f"w={w:.1f}\xb0, \u03b4={delta:.1f}\xb0"

    def generate_ssp_values(self) -> str:
        lam = self._rng.uniform(-180, 180)
        beta = self._rng.uniform(-90, 90)
        return f"\u03bb={lam:.1f}\xb0, \u00df={beta:.1f}\xb0"

    def generate_np_value(self) -> str:
        return f"{self._rng.uniform(0.5, 1.0):.2f}"

    def generate_arcseconds(self) -> str:
        return f"{self._rng.uniform(0.1, 1.0):.2f}\""

    def generate_all(self) -> dict[str, str]:
        return {
            "pole": self.generate_pole_coordinates(),
            "sep": self.generate_sep_values(),
            "ssp": self.generate_ssp_values(),
            "np": self.generate_np_value(),
            "arc": self.generate_arcseconds(),
        }
