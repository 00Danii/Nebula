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
        bg = self._blend_bg(bg_color) if bg_color else None

        if inside:
            w = self._img_w(image_rect, width)
            h = self._img_h(image_rect, height)
            ox, oy = self._img_offset(image_rect, 0, 0)
            self._draw_pole(draw, data, color, font_main, font_small, bg, ox, oy, True)
            self._draw_bottom_left(draw, h, data, color, font_main, font_small, bg, ox, oy, True)
            self._draw_arcseconds(draw, w, h, data, color, font_main, bg, ox, oy, True)
        elif image_rect is not None and image_rect[2] < image_rect[3]:
            self._draw_outside_portrait(draw, width, height, data, color, font_main, font_small, bg, image_rect)
        else:
            self._draw_pole(draw, data, color, font_main, font_small, bg, 0, 0, False)
            self._draw_bottom_left(draw, height, data, color, font_main, font_small, bg, 0, 0, False)
            self._draw_arcseconds(draw, width, height, data, color, font_main, bg, 0, 0, False)

    def _draw_outside_portrait(self, draw, width, height, data, color, font_main, font_small, bg, image_rect):
        x_left = 30

        pole_parts = data["pole"].split(", ")
        y_pole = 30
        if bg:
            label = "Pole (ECJ2000):"
            b_label = draw.textbbox((0, 0), label, font=font_main)
            b_r1 = draw.textbbox((0, 0), pole_parts[0], font=font_small)
            b_r2 = draw.textbbox((0, 0), pole_parts[1], font=font_small) if len(pole_parts) > 1 else b_r1
            tw = max(b_label[2] - b_label[0], b_r1[2] - b_r1[0], b_r2[2] - b_r2[0])
            th_small = b_r1[3] - b_r1[1]
            draw.rectangle(
                (x_left - 4, y_pole - 3, x_left + tw + 4, y_pole + 25 + th_small + 5 + th_small + 3),
                fill=bg,
            )
        draw.text((x_left, y_pole), "Pole (ECJ2000):", fill=color, font=font_main)
        draw.text((x_left, y_pole + 25), pole_parts[0], fill=color, font=font_small)
        draw.text((x_left, y_pole + 25 + 22), pole_parts[1], fill=color, font=font_small)

        sep_parts = data["sep"].split(", ")
        ssp_parts = data["ssp"].split(", ")
        x = x_left
        lines = [
            ("SEP (w,\u03b4):", font_main, 0, 0),
            (sep_parts[0], font_small, 0, 22),
            (sep_parts[1], font_small, 0, 44) if len(sep_parts) > 1 else ("", font_small, 0, 44),
            ("SSP (\u03bb,\u00df):", font_main, 0, 74),
            (ssp_parts[0], font_small, 0, 96),
            (ssp_parts[1], font_small, 0, 118) if len(ssp_parts) > 1 else ("", font_small, 0, 118),
            ("NP:", font_main, 0, 148),
            (f"{data['np']}", font_main, 35, 148),
        ]
        last_line = lines[-1]
        b_last = draw.textbbox((0, 0), last_line[0], font=last_line[1])
        total_h = lines[-1][3] + (b_last[3] - b_last[1])
        y_offset = height - total_h - 10
        if bg:
            max_w = 0
            first_y = y_offset + lines[0][3]
            last_y = y_offset + total_h
            for text, font, dx, dy in lines:
                if not text:
                    continue
                b = draw.textbbox((0, 0), text, font=font)
                tw = (b[2] - b[0]) + dx
                if tw > max_w:
                    max_w = tw
            draw.rectangle(
                (x - 4, first_y - 3, x + max_w + 4, last_y + 3),
                fill=bg,
            )
        for text, font, dx, dy in lines:
            if not text:
                continue
            draw.text((x + dx, y_offset + dy), text, fill=color, font=font)

        label = f"arcsecond: {data['arc']}"
        bbox = draw.textbbox((0, 0), label, font=font_main)
        tw = bbox[2] - bbox[0]
        ty = bbox[3] - bbox[1]
        x_right = width - tw - 30
        y_arc = height - 30
        self._text_bg(draw, x_right, y_arc, label, font_main, bg)
        draw.text((x_right, y_arc), label, fill=color, font=font_main)

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
        x = ox + (6 if inside else 30)
        lines = [
            ("SEP (w,\u03b4):", font_main, 0, 0),
            (f"{data['sep']}", font_small, 0, 22),
            ("SSP (\u03bb,\u00df):", font_main, 0, 52),
            (f"{data['ssp']}", font_small, 0, 74),
            ("NP:", font_main, 0, 98),
            (f"{data['np']}", font_main, 35, 98),
        ]
        last_line = lines[-1]
        b_last = draw.textbbox((0, 0), last_line[0], font=last_line[1])
        total_h = lines[-1][3] + (b_last[3] - b_last[1])
        y_offset = oy + height - total_h - (6 if inside else 10)
        if bg:
            max_w = 0
            first_y = y_offset + lines[0][3]
            last_y = y_offset + total_h
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
