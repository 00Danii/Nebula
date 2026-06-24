import math
import random
from PIL import ImageDraw
from metadata_styles.base_metadata_style import BaseMetadataStyle


class AlienHUDMetadataStyle(BaseMetadataStyle):
    @property
    def id(self) -> str:
        return "alien_hud"

    @property
    def name(self) -> str:
        return "HUD Alien\u00edgena"

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
            self._draw_corner_brackets(draw, w, h, color, ox, oy)
            self._draw_radar(draw, data, color, font_small, bg, ox, oy, True)
            self._draw_decoded_data(draw, h, data, color, font_main, font_small, bg, ox, oy, True)
            self._draw_frequency_bar(draw, w, h, data, color, font_small, bg, ox, oy, True)
        elif image_rect is not None and image_rect[2] < image_rect[3]:
            self._draw_outside_portrait(draw, width, height, data, color, font_main, font_small, bg, image_rect)
        else:
            self._draw_corner_brackets(draw, width, height, color, 0, 0)
            self._draw_radar(draw, data, color, font_small, bg, 0, 0, False)
            self._draw_decoded_data(draw, height, data, color, font_main, font_small, bg, 0, 0, False)
            self._draw_frequency_bar(draw, width, height, data, color, font_small, bg, 0, 0, False)

    def _draw_outside_portrait(self, draw, width, height, data, color, font_main, font_small, bg, image_rect):
        self._draw_corner_brackets(draw, width, height, color, 0, 0)
        self._draw_radar(draw, data, color, font_small, bg, 0, 0, False)
        self._draw_decoded_data(draw, height, data, color, font_main, font_small, bg, 0, 0, False)
        self._draw_frequency_bar(draw, width, height, data, color, font_small, bg, 0, 0, False)

    def _draw_corner_brackets(self, draw, width, height, color, ox, oy):
        accent = (
            min(255, color[0] + 100),
            min(255, color[1] + 100),
            min(255, color[2] + 100),
        )
        m = 15
        bs = 25

        draw.line((ox + m, oy + m + bs, ox + m, oy + m), fill=color, width=2)
        draw.line((ox + m, oy + m, ox + m + bs, oy + m), fill=color, width=2)
        draw.ellipse((ox + m + bs // 2 - 2, oy + m - 2, ox + m + bs // 2 + 2, oy + m + 2), fill=accent)

        draw.line((ox + width - m - bs, oy + m, ox + width - m, oy + m), fill=color, width=2)
        draw.line((ox + width - m, oy + m, ox + width - m, oy + m + bs), fill=color, width=2)
        draw.ellipse((ox + width - m - bs // 2 - 2, oy + m - 2, ox + width - m - bs // 2 + 2, oy + m + 2), fill=accent)

        draw.line((ox + m, oy + height - m - bs, ox + m, oy + height - m), fill=color, width=2)
        draw.line((ox + m, oy + height - m, ox + m + bs, oy + height - m), fill=color, width=2)
        draw.ellipse((ox + m + bs // 2 - 2, oy + height - m - 2, ox + m + bs // 2 + 2, oy + height - m + 2), fill=accent)

        draw.line((ox + width - m, oy + height - m - bs, ox + width - m, oy + height - m), fill=color, width=2)
        draw.line((ox + width - m - bs, oy + height - m, ox + width - m, oy + height - m), fill=color, width=2)
        draw.ellipse((ox + width - m - bs // 2 - 2, oy + height - m - 2, ox + width - m - bs // 2 + 2, oy + height - m + 2), fill=accent)

        draw.line((ox + m + bs, oy + m, ox + width - m - bs, oy + m), fill=color, width=1)

    def _draw_radar(self, draw, data, color, font_small, bg, ox, oy, inside):
        x = ox + (20 if inside else 40)
        y = oy + (20 if inside else 40)
        r = 35
        cx, cy = x + r, y + r

        if bg:
            draw.ellipse((cx - r - 4, cy - r - 4, cx + r + 4, cy + r + 4), fill=bg)

        draw.ellipse((cx - r, cy - r, cx + r, cy + r), outline=color, width=2)
        draw.ellipse((cx - r // 2, cy - r // 2, cx + r // 2, cy + r // 2), outline=color, width=1)

        draw.line((cx - r + 4, cy, cx + r - 4, cy), fill=color, width=1)
        draw.line((cx, cy - r + 4, cx, cy + r - 4), fill=color, width=1)

        np_val = float(data["np"])
        sweep_deg = np_val * 180.0
        sweep_angle = math.radians(sweep_deg)
        sweep_x = cx + r * math.cos(sweep_angle)
        sweep_y = cy - r * math.sin(sweep_angle)
        draw.line((cx, cy, sweep_x, sweep_y), fill=color, width=2)

        r_spot = 3
        draw.ellipse((cx - r_spot, cy - r_spot, cx + r_spot, cy + r_spot), fill=color)

        for text, dx, dy in [("N", 0, -r - 8), ("S", 0, r + 6), ("E", r + 6, 0), ("W", -r - 10, 0)]:
            b = draw.textbbox((0, 0), text, font=font_small)
            tw = b[2] - b[0]
            th = b[3] - b[1]
            draw.text((cx + dx - tw // 2, cy + dy - th // 2), text, fill=color, font=font_small)

        label = "SIG"
        b_box = draw.textbbox((0, 0), label, font=font_small)
        lw = b_box[2] - b_box[0]
        draw.text((cx - lw // 2, cy + r + 10), label, fill=color, font=font_small)

    def _draw_decoded_data(self, draw, height, data, color, font_main, font_small, bg, ox, oy, inside):
        x = ox + (20 if inside else 40)

        pole_parts = data["pole"].split(", ")
        sep_parts = data["sep"].split(", ")
        ssp_parts = data["ssp"].split(", ")

        lines = []
        lines.append(("> DECODIFICANDO...", font_small))
        lines.append(("", font_small))
        lines.append((f"  SRC: {pole_parts[0]}", font_small))
        if len(pole_parts) > 1:
            lines.append((f"  TRK: {pole_parts[1]}", font_small))
        lines.append(("", font_small))
        lines.append((f"  SEP: {sep_parts[0]}", font_small))
        if len(sep_parts) > 1:
            lines.append((f"  DEL: {sep_parts[1]}", font_small))
        lines.append(("", font_small))
        lines.append((f"  SSP: {ssp_parts[0]}", font_small))
        if len(ssp_parts) > 1:
            lines.append((f"  ANG: {ssp_parts[1]}", font_small))
        lines.append(("", font_small))
        lines.append((f"  NP: {data['np']}", font_main))
        lines.append((f"  RES: {data['arc']}", font_small))

        total_h = 0
        for text, font in lines:
            b = draw.textbbox((0, 0), text, font=font)
            total_h += (b[3] - b[1]) + 3

        y = oy + height - total_h - (20 if inside else 40)
        y_start = y

        max_w = 0
        for text, font in lines:
            if text:
                b = draw.textbbox((0, 0), text, font=font)
                tw = b[2] - b[0]
                if tw > max_w:
                    max_w = tw
        draw.rectangle(
            (x - 6, y_start - 6, x + max_w + 12, y_start + total_h + 8),
            fill=(0, 0, 0),
        )

        accent = (
            min(255, color[0] + 100),
            min(255, color[1] + 100),
            min(255, color[2] + 100),
        )

        cursor_x = x + 4
        cursor_y = y_start + 2
        draw.rectangle((cursor_x, cursor_y, cursor_x + 6, cursor_y + 10), fill=accent)

        for text, font in lines:
            b = draw.textbbox((0, 0), text, font=font)
            th = b[3] - b[1]
            draw.text((x + 12, y), text, fill=color, font=font)
            y += th + 3

        line_y = y_start + total_h + 8
        draw.line((x, line_y, x + 220, line_y), fill=color, width=1)

    def _draw_frequency_bar(self, draw, width, height, data, color, font_small, bg, ox, oy, inside):
        bar_w = min(250, width - 80)
        bar_h = 14
        x = ox + width // 2 - bar_w // 2
        y = oy + height - (25 if inside else 45)

        if bg:
            draw.rectangle((x - 4, y - 4, x + bar_w + 4, y + bar_h + 4), fill=bg)

        draw.rectangle((x, y, x + bar_w, y + bar_h), outline=color, width=1)

        num_bars = 24
        seg_w = (bar_w - 2) / num_bars
        np_val = float(data["np"])
        rng = random.Random(str(np_val) + data["arc"])

        for i in range(num_bars):
            val = 0.25 + 0.75 * abs(math.sin(i * 0.8 + np_val * 5))
            val = val * (0.7 + 0.3 * rng.random())
            seg_h = val * (bar_h - 4)
            sx = x + 2 + int(i * seg_w)
            sy = y + bar_h - 2 - seg_h
            brightness = 0.4 + 0.6 * val
            seg_color = (
                int(color[0] * brightness),
                int(color[1] * brightness),
                int(color[2] * brightness),
            )
            draw.rectangle(
                (sx, sy, sx + int(seg_w) - 1, y + bar_h - 2),
                fill=seg_color,
            )

        label = f"FREQ: {data['arc']}"
        b = draw.textbbox((0, 0), label, font=font_small)
        tw = b[2] - b[0]
        draw.text((x + bar_w // 2 - tw // 2, y - 18), label, fill=color, font=font_small)
