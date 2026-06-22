from PIL import ImageDraw
from utils.font_utils import FontManager
from metadata_styles import MetadataStyleManager


class MetadataRenderer:
    def __init__(self):
        self._font_manager = FontManager()
        self._font_path: str | None = None
        self.font_size_main: int = 16
        self.font_size_small: int = 12
        self._style_manager = MetadataStyleManager()
        self._style_id: str = "minimal"

    @property
    def font_path(self) -> str | None:
        return self._font_path

    @font_path.setter
    def font_path(self, path: str | None):
        self._font_path = path
        self._font_manager.clear_cache()

    @property
    def style_id(self) -> str:
        return self._style_id

    @style_id.setter
    def style_id(self, value: str):
        if self._style_manager.get(value):
            self._style_id = value

    def list_styles(self) -> list[dict]:
        return self._style_manager.list_styles()

    def render(self, draw: ImageDraw.ImageDraw, width: int, height: int, data: dict, color, bg_color: tuple[int, int, int] | None = None, image_rect: tuple[int, int, int, int] | None = None, position: str = "outside"):
        style = self._style_manager.get(self._style_id)
        if not style:
            style = self._style_manager.get("minimal")

        font_main = self._font_manager.load(self._font_path, self.font_size_main)
        font_small = self._font_manager.load(self._font_path, self.font_size_small)

        style.render(draw, width, height, data, color, font_main, font_small, bg_color=bg_color, image_rect=image_rect, position=position)
