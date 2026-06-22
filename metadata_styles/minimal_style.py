from PIL import ImageDraw
from metadata_styles.base_metadata_style import BaseMetadataStyle


class MinimalMetadataStyle(BaseMetadataStyle):
    @property
    def id(self) -> str:
        return "minimal"

    @property
    def name(self) -> str:
        return "Minimal"

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
        inside = position == "inside" and image_rect is not None
        w = self._img_w(image_rect, width) if inside else width
        h = self._img_h(image_rect, height) if inside else height
        ox, oy = self._img_offset(image_rect, 0, 0) if inside else (0, 0)
        bg = self._blend_bg(bg_color) if bg_color else None

        self._draw_pole(draw, data, color, font_main, font_small, bg, ox, oy)
        self._draw_bottom_left(draw, h, data, color, font_main, font_small, bg, ox, oy)
        self._draw_arcseconds(draw, w, h, data, color, font_main, bg, ox, oy)

    def _draw_pole(self, draw, data, color, font_main, font_small, bg, ox, oy):
        x, y = ox + 10, oy + 10
        self._text_bg(draw, x, y, "Pole (ECJ2000):", font_main, bg)
        draw.text((x, y), "Pole (ECJ2000):", fill=color, font=font_main)
        self._text_bg(draw, x, y + 25, f"{data['pole']}", font_small, bg)
        draw.text((x, y + 25), f"{data['pole']}", fill=color, font=font_small)

    def _draw_bottom_left(self, draw, height, data, color, font_main, font_small, bg, ox, oy):
        y_offset = oy + height - 130
        x = ox + 10
        self._text_bg(draw, x, y_offset, "SEP (w,\u03b4):", font_main, bg)
        draw.text((x, y_offset), "SEP (w,\u03b4):", fill=color, font=font_main)
        sep_val = f"{data['sep']}"
        self._text_bg(draw, x, y_offset + 22, sep_val, font_small, bg)
        draw.text((x, y_offset + 22), sep_val, fill=color, font=font_small)

        self._text_bg(draw, x, y_offset + 52, "SSP (\u03bb,\u00df):", font_main, bg)
        draw.text((x, y_offset + 52), "SSP (\u03bb,\u00df):", fill=color, font=font_main)
        ssp_val = f"{data['ssp']}"
        self._text_bg(draw, x, y_offset + 74, ssp_val, font_small, bg)
        draw.text((x, y_offset + 74), ssp_val, fill=color, font=font_small)

        self._text_bg(draw, x, y_offset + 98, "NP:", font_main, bg)
        draw.text((x, y_offset + 98), "NP:", fill=color, font=font_main)
        np_val = f"{data['np']}"
        self._text_bg(draw, x + 35, y_offset + 98, np_val, font_main, bg)
        draw.text((x + 35, y_offset + 98), np_val, fill=color, font=font_main)

    def _draw_arcseconds(self, draw, width, height, data, color, font_main, bg, ox, oy):
        label = f"arcsecond: {data['arc']}"
        bbox = draw.textbbox((0, 0), label, font=font_main)
        tw = bbox[2] - bbox[0]
        x = ox + width - tw - 10
        y = oy + height - 30
        self._text_bg(draw, x, y, label, font_main, bg)
        draw.text((x, y), label, fill=color, font=font_main)
