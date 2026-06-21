from styles.base_style import BaseStyle
from styles.sepia_style import SepiaStyle
from styles.crt_style import CRTStyle
from styles.thermal_style import ThermalStyle
from styles.noir_style import NoirStyle
from styles.creative_styles import (
    CyberpunkStyle, VaporwaveStyle, GoldStyle, IceStyle,
    PastelStyle, MutedStyle, InvertStyle, NeonStyle, DuotoneStyle,
    TritoneStyle,
)
from styles.custom_style import CustomStyle


class StyleManager:
    def __init__(self):
        self._styles: dict[str, BaseStyle] = {}
        self._register_defaults()

    def _register_defaults(self):
        self.register(SepiaStyle())
        self.register(CRTStyle())
        self.register(ThermalStyle())
        self.register(NoirStyle())
        self.register(CyberpunkStyle())
        self.register(VaporwaveStyle())
        self.register(GoldStyle())
        self.register(IceStyle())
        self.register(PastelStyle())
        self.register(MutedStyle())
        self.register(InvertStyle())
        self.register(NeonStyle())
        self.register(DuotoneStyle())
        self.register(TritoneStyle())
        self.register(CustomStyle())

    def register(self, style: BaseStyle):
        self._styles[style.id] = style

    def get(self, style_id: str) -> BaseStyle | None:
        return self._styles.get(style_id)

    def list_styles(self) -> list[dict]:
        return [
            {
                "id": sid,
                "name": s.name,
                "colors": s.get_editable_colors(),
                "params": s.get_style_params(),
                "param_groups": s.get_style_param_groups(),
            }
            for sid, s in self._styles.items()
        ]

    def update_style_color(self, style_id: str, color_key: str, value: tuple[int, int, int]):
        style = self.get(style_id)
        if style:
            style.update_color(color_key, value)

    def update_style_param(self, style_id: str, param_name: str, value):
        style = self.get(style_id)
        if style:
            style.update_style_param(param_name, value)

    def reset_style(self, style_id: str):
        if style_id in self._styles:
            cls = self._styles[style_id].__class__
            self._styles[style_id] = cls()
