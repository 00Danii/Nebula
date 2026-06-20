from styles.base_style import BaseStyle
from styles.sepia_style import SepiaStyle
from styles.crt_style import CRTStyle
from styles.thermal_style import ThermalStyle


class StyleManager:
    def __init__(self):
        self._styles: dict[str, BaseStyle] = {}
        self._register_defaults()

    def _register_defaults(self):
        self.register(SepiaStyle())
        self.register(CRTStyle())
        self.register(ThermalStyle())

    def register(self, style: BaseStyle):
        self._styles[style.id] = style

    def get(self, style_id: str) -> BaseStyle | None:
        return self._styles.get(style_id)

    def list_styles(self) -> list[dict]:
        return [
            {"id": sid, "name": s.name, "colors": s.get_editable_colors()}
            for sid, s in self._styles.items()
        ]

    def update_style_color(self, style_id: str, color_key: str, value: tuple[int, int, int]):
        style = self.get(style_id)
        if style:
            style.update_color(color_key, value)
