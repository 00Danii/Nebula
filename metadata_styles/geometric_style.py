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

        margin = 8 if inside else 80
        self._draw_crosshair(draw, w, h, margin, data, color, font_small, bg, ox, oy)
        self._draw_angle_arcs(draw, h, data, color, font_main, font_small, bg, ox)
        self._draw_dial_gauge(draw, h, data, color, font_main, font_small, bg, ox, oy)
        self._draw_tick_marks(draw, w, h, data, color, font_small, bg, ox, oy)

    def _draw_crosshair(self, draw, width, height, margin, data, color, font_small, bg, ox, oy):
        cx, cy = ox + width // 2, oy + height // 2
        draw.line((ox + margin, cy, ox + width - margin, cy), fill=color, width=1)
        draw.line((cx, oy + margin, cx, oy + height - margin), fill=color, width=1)

        draw.line((cx - 6, cy, cx + 6, cy), fill=color, width=2)
        draw.line((cx, cy - 6, cx, cy + 6), fill=color, width=2)

        pole = data["pole"]
        px = cx + 10
        py = oy + margin - 8
        if bg:
            self._text_bg(draw, px, py, pole, font_small, bg)
        draw.text((px, py), pole, fill=color, font=font_small)

    def _draw_angle_arcs(self, draw, height, data, color, font_main, font_small, bg, ox):
        base_x, base_y = ox + 30, height - 170
        r = 38
        gap = 115

        for i, (label, key) in enumerate([("SEP", "sep"), ("SSP", "ssp")]):
            cx = base_x + gap * i + r
            cy = base_y + r

            if bg:
                draw.rectangle(
                    (cx - r - 10, cy - r - 10, cx + r + 16, cy + r + 42),
                    fill=bg,
                )

            draw.arc(
                (cx - r, cy - r, cx + r, cy + r),
                start=0, end=180,
                fill=color, width=2,
            )
            draw.line((cx - r, cy, cx + r, cy), fill=color, width=1)
            draw.line((cx, cy, cx + r, cy), fill=color, width=2)

            val = data[key]
            if bg:
                self._text_bg(draw, cx - r, cy + r + 8, f"{label}:", font_small, bg)
                self._text_bg(draw, cx - r, cy + r + 24, val, font_small, bg)
            draw.text((cx - r, cy + r + 8), f"{label}:", fill=color, font=font_small)
            draw.text((cx - r, cy + r + 24), val, fill=color, font=font_small)

    def _draw_dial_gauge(self, draw, height, data, color, font_main, font_small, bg, ox, oy):
        cx, cy = ox + 170, height - 65
        r = 26

        if bg:
            draw.rectangle(
                (cx - r - 10, cy - r - 10, cx + r + 30, cy + r + 14),
                fill=bg,
            )

        draw.arc(
            (cx - r, cy - r, cx + r, cy + r),
            start=0, end=180,
            fill=color, width=3,
        )
        draw.line((cx - r, cy, cx + r, cy), fill=color, width=1)

        np_val = float(data["np"])
        angle = 180 * (np_val - 0.5) / 0.5
        rad = math.radians(180 - angle)
        nx = cx + (r - 6) * math.cos(rad)
        ny = cy - (r - 6) * math.sin(rad)
        draw.line((cx, cy, nx, ny), fill=color, width=2)

        np_label = f"NP {data['np']}"
        if bg:
            self._text_bg(draw, cx - 12, cy + 6, np_label, font_small, bg)
        draw.text((cx - 12, cy + 6), np_label, fill=color, font=font_small)

    def _draw_tick_marks(self, draw, width, height, data, color, font_small, bg, ox, oy):
        y = oy + height - 12
        x_start = ox + width - 190
        x_end = ox + width - 14
        num_ticks = 5

        if bg:
            draw.rectangle(
                (x_start - 6, y - 24, x_end + 6, y + 8),
                fill=bg,
            )

        draw.line((x_start, y, x_end, y), fill=color, width=1)

        for i in range(num_ticks):
            x = x_start + (x_end - x_start) * i // (num_ticks - 1)
            tick_h = 8 if i % 2 == 0 else 4
            draw.line((x, y - tick_h, x, y + tick_h), fill=color, width=1)

        label = f"arcsecond: {data['arc']}"
        bbox = draw.textbbox((0, 0), label, font=font_small)
        tw = bbox[2] - bbox[0]
        lx = x_start + (x_end - x_start) // 2 - tw // 2
        ly = y - 22
        if bg:
            self._text_bg(draw, lx, ly, label, font_small, bg)
        draw.text((lx, ly), label, fill=color, font=font_small)
