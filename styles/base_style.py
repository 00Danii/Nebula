from abc import ABC, abstractmethod
from PIL import Image, ImageDraw


class BaseStyle(ABC):
    def __init__(self):
        self._palette: dict[str, tuple[int, int, int]] = {}
        self._background_color: tuple[int, int, int] = (0, 0, 0)

    @property
    @abstractmethod
    def id(self) -> str: ...

    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    def background_color(self) -> tuple[int, int, int]:
        return self._background_color

    @abstractmethod
    def get_palette(self) -> dict[str, tuple[int, int, int]]: ...

    @abstractmethod
    def process_subject(self, image: Image.Image) -> Image.Image: ...

    def apply_post_effects(self, canvas: Image.Image, draw: ImageDraw.ImageDraw, size: tuple[int, int]):
        pass

    def update_color(self, key: str, value: tuple[int, int, int]):
        if key in self._palette:
            self._palette[key] = value

    def get_editable_colors(self) -> dict[str, tuple[int, int, int]]:
        return dict(self._palette)

    def get_style_params(self) -> dict[str, dict]:
        return {}

    def get_style_param_groups(self) -> list[dict] | None:
        return None

    def update_style_param(self, name: str, value):
        pass
