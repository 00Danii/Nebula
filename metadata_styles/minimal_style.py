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

        self._draw_pole(draw, data, color, font_main, font_small, bg, ox, oy, inside)
        self._draw_bottom_left(draw, h, data, color, font_main, font_small, bg, ox, oy, inside)
        self._draw_arcseconds(draw, w, h, data, color, font_main, bg, ox, oy, inside)

    def _draw_pole(self, draw, data, color, font_main, font_small, bg, ox, oy, inside):
        x, y = ox + (6 if inside else 30), oy + (5 if inside else 30)
        if bg:
            line1 = "Pole (ECJ2000):"
            line2 = f"{data['pole']}"
            b1 = draw.textbbox((0, 0), line1, font=font_main)
            b2 = draw.textbbox((0, 0), line2, font=font_small)
            tw = max(b1[2] - b1[0], b2[2] - b2[0])
            th1 = b1[3] - b1[1]
            th2 = b2[3] - b2[1]
            draw.rectangle(
                (x - 4, y - 3, x + tw + 4, y + 25 + th2 + 3),
                fill=bg,
            )
        draw.text((x, y), "Pole (ECJ2000):", fill=color, font=font_main)
        draw.text((x, y + 25), f"{data['pole']}", fill=color, font=font_small)

    def _draw_bottom_left(self, draw, height, data, color, font_main, font_small, bg, ox, oy, inside):
        y_offset = oy + height - 130
        x = ox + (6 if inside else 30)
        lines = [
            ("SEP (w,\u03b4):", font_main, 0, 0),
            (f"{data['sep']}", font_small, 0, 22),
            ("SSP (\u03bb,\u00df):", font_main, 0, 52),
            (f"{data['ssp']}", font_small, 0, 74),
            ("NP:", font_main, 0, 98),
            (f"{data['np']}", font_main, 35, 98),
        ]
        if bg:
            max_w = 0
            first_y = y_offset + lines[0][3]
            last_line = lines[-1]
            b_last = draw.textbbox((0, 0), last_line[0], font=last_line[1])
            last_y = y_offset + last_line[3] + (b_last[3] - b_last[1])
            for text, font, dx, dy in lines:
                b = draw.textbbox((0, 0), text, font=font)
                tw = (b[2] - b[0]) + dx
                if tw > max_w:
                    max_w = tw
            draw.rectangle(
                (x - 4, first_y - 3, x + max_w + 4, last_y + 3),
                fill=bg,
            )
        for text, font, dx, dy in lines:
            draw.text((x + dx, y_offset + dy), text, fill=color, font=font)

    def _draw_arcseconds(self, draw, width, height, data, color, font_main, bg, ox, oy, inside):
        label = f"arcsecond: {data['arc']}"
        bbox = draw.textbbox((0, 0), label, font=font_main)
        tw = bbox[2] - bbox[0]
        ty = bbox[3] - bbox[1]
        x = ox + width - tw - (6 if inside else 10)
        y = oy + height - (ty + 5 if inside else 30)
        self._text_bg(draw, x, y, label, font_main, bg)
        draw.text((x, y), label, fill=color, font=font_main)
