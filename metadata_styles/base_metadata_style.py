from abc import ABC, abstractmethod
from PIL import ImageDraw


class BaseMetadataStyle(ABC):
    @property
    @abstractmethod
    def id(self) -> str:
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @abstractmethod
    def render(
        self,
        draw: ImageDraw.ImageDraw,
        width: int,
        height: int,
        data: dict,
        color: tuple[int, int, int],
        font_main,
        font_small,
        bg_color: tuple[int, int, int] | None = None,
        image_rect: tuple[int, int, int, int] | None = None,
        position: str = "outside",
    ):
        ...

    def _text_bg(self, draw, x, y, text, font, bg_color, pad_x=4, pad_y=2):
        if bg_color is None:
            return
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        draw.rectangle(
            (x - pad_x, y - pad_y, x + tw + pad_x, y + th + pad_y),
            fill=bg_color,
        )

    def _blend_bg(self, bg_color: tuple[int, int, int], alpha: float = 0.7) -> tuple[int, int, int]:
        return (
            int(bg_color[0] * alpha),
            int(bg_color[1] * alpha),
            int(bg_color[2] * alpha),
        )

    def _img_offset(self, image_rect: tuple[int, int, int, int] | None, x: int, y: int) -> tuple[int, int]:
        if image_rect is None:
            return (x, y)
        return (image_rect[0] + x, image_rect[1] + y)

    def _img_w(self, image_rect: tuple[int, int, int, int] | None, canvas_w: int) -> int:
        if image_rect is None:
            return canvas_w
        return image_rect[2]

    def _img_h(self, image_rect: tuple[int, int, int, int] | None, canvas_h: int) -> int:
        if image_rect is None:
            return canvas_h
        return image_rect[3]
