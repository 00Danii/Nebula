import math
from PIL import ImageDraw
from metadata_styles.base_metadata_style import BaseMetadataStyle


class GeometricMetadataStyle(BaseMetadataStyle):
    @property
    def id(self) -> str:
        return "geometric"

    @property
    def name(self) -> str:
        return "Geom\u00e9trico"

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

        margin = 16 if inside else 80
        self._draw_crosshair(draw, w, h, margin, data, color, font_small, bg, ox, oy, inside)
        self._draw_bottom_left(draw, h, data, color, font_main, font_small, bg, ox, oy, inside)
        self._draw_tick_marks(draw, w, h, data, color, font_small, bg, ox, oy, inside)

    def _draw_crosshair(self, draw, width, height, margin, data, color, font_small, bg, ox, oy, inside):
        cx, cy = ox + width // 2, oy + height // 2
        cr = min(width, height) // 2 - margin

        draw.line((ox + margin, cy, ox + width - margin, cy), fill=color, width=1)
        draw.line((cx, oy + margin, cx, oy + height - margin), fill=color, width=1)

        if inside and cr > 20:
            draw.ellipse((cx - cr, cy - cr, cx + cr, cy + cr), outline=color, width=1)
            for deg in range(0, 360, 30):
                rad = math.radians(deg)
                r1 = cr
                r2 = cr - 6 if deg % 90 == 0 else cr - 4
                x1 = cx + r1 * math.cos(rad)
                y1 = cy + r1 * math.sin(rad)
                x2 = cx + r2 * math.cos(rad)
                y2 = cy + r2 * math.sin(rad)
                draw.line((x1, y1, x2, y2), fill=color, width=1)

        draw.line((cx - 8, cy, cx + 8, cy), fill=color, width=2)
        draw.line((cx, cy - 8, cx, cy + 8), fill=color, width=2)

        pole = data["pole"]
        if inside:
            px = ox + 6
            py = oy + 5
        else:
            px = cx - cr + 6
            py = cy - cr - 16
        if bg:
            self._text_bg(draw, px, py, pole, font_small, bg)
        draw.text((px, py), pole, fill=color, font=font_small)

    def _draw_bottom_left(self, draw, height, data, color, font_main, font_small, bg, ox, oy, inside):
        x = ox + (20 if inside else 30)
        r_arc = 36
        r_dial = 24
        gap = 110
        spacing = 10

        b_small = draw.textbbox((0, 0), "Tg", font=font_small)
        th = b_small[3] - b_small[1]

        arc_row_h = 2 * r_arc + (8 + th if inside else 24 + th)
        np_text = f"NP {data['np']}"
        b_np = draw.textbbox((0, 0), np_text, font=font_small)
        np_tw = b_np[2] - b_np[0]
        np_th = b_np[3] - b_np[1]
        dial_h = r_dial + 40 + np_th
        total_h = arc_row_h + spacing + dial_h

        y_offset = oy + height - total_h - (6 if inside else 10)

        arc_cy = y_offset + r_arc
        dial_cy = y_offset + arc_row_h + spacing + r_dial

        if not inside:
            for i, (label, key) in enumerate([("SEP", "sep"), ("SSP", "ssp")]):
                arc_cx = x + gap * i + r_arc
                val = data[key]
                
                b_val = draw.textbbox((0, 0), val, font=font_small)
                b_lbl = draw.textbbox((0, 0), f"{label}:", font=font_small)
                text_w = max(b_lbl[2] - b_lbl[0], b_val[2] - b_val[0])

                if bg:
                    draw.rectangle(
                        (arc_cx - r_arc - 10, arc_cy - r_arc - 10, arc_cx + r_arc + 16, arc_cy + r_arc + 42),
                        fill=bg,
                    )

                draw.arc((arc_cx - r_arc, arc_cy - r_arc, arc_cx + r_arc, arc_cy + r_arc), start=0, end=180, fill=color, width=2)
                draw.line((arc_cx - r_arc, arc_cy, arc_cx + r_arc, arc_cy), fill=color, width=1)
                mid_rad = math.radians(90)
                mx = arc_cx + r_arc * math.cos(mid_rad)
                my = arc_cy - r_arc * math.sin(mid_rad)
                draw.line((arc_cx, arc_cy, mx, my), fill=color, width=2)
                draw.text((arc_cx - text_w // 2, arc_cy + r_arc + 8), f"{label}:", fill=color, font=font_small)
                draw.text((arc_cx - text_w // 2, arc_cy + r_arc + 24), val, fill=color, font=font_small)

        dial_cx = x + r_dial

        if bg:
            draw.rectangle(
                (dial_cx - r_dial - 10, dial_cy - r_dial - 10, dial_cx + max(r_dial + 10, np_tw // 2 + 10), dial_cy + 40 + np_th + 4),
                fill=bg,
            )

        draw.arc((dial_cx - r_dial, dial_cy - r_dial, dial_cx + r_dial, dial_cy + r_dial), start=0, end=180, fill=color, width=3)
        draw.line((dial_cx - r_dial, dial_cy, dial_cx + r_dial, dial_cy), fill=color, width=1)

        for val in [0.5, 0.75, 1.0]:
            a = 180 * (val - 0.5) / 0.5
            rad = math.radians(180 - a)
            tk_x = dial_cx + (r_dial - 4) * math.cos(rad)
            tk_y = dial_cy - (r_dial - 4) * math.sin(rad)
            tk_x2 = dial_cx + (r_dial - 10) * math.cos(rad)
            tk_y2 = dial_cy - (r_dial - 10) * math.sin(rad)
            draw.line((tk_x, tk_y, tk_x2, tk_y2), fill=color, width=1)

        np_val = float(data["np"])
        angle = 180 * (np_val - 0.5) / 0.5
        rad = math.radians(180 - angle)
        nx = dial_cx + (r_dial - 4) * math.cos(rad)
        ny = dial_cy - (r_dial - 4) * math.sin(rad)
        draw.line((dial_cx, dial_cy, nx, ny), fill=color, width=2)
        draw.text((dial_cx - np_tw // 2, dial_cy + 40), np_text, fill=color, font=font_small)

    def _draw_tick_marks(self, draw, width, height, data, color, font_small, bg, ox, oy, inside):
        arc_str = data["arc"]
        label = f"arcsecond: {arc_str}"
        bbox = draw.textbbox((0, 0), label, font=font_small)
        tw = bbox[2] - bbox[0]
        ty = bbox[3] - bbox[1]

        bar_w = 160
        pad_right = 6 if inside else 10
        bar_x = ox + width - bar_w - pad_right
        bar_y = oy + height - (ty + 5 if inside else 30)
        num_ticks = 5

        if bg:
            draw.rectangle(
                (bar_x - 6, bar_y - 22, bar_x + bar_w + 6, bar_y + 10),
                fill=bg,
            )

        draw.line((bar_x, bar_y, bar_x + bar_w, bar_y), fill=color, width=1)

        for i in range(num_ticks):
            x = bar_x + bar_w * i // (num_ticks - 1)
            tick_h = 8 if i % 2 == 0 else 4
            draw.line((x, bar_y - tick_h, x, bar_y + tick_h), fill=color, width=1)

        lx = bar_x + bar_w // 2 - tw // 2
        ly = bar_y - 20
        draw.text((lx, ly), label, fill=color, font=font_small)
