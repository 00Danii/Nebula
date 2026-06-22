from PIL import ImageDraw
from metadata_styles.base_metadata_style import BaseMetadataStyle


class ScientificHUDMetadataStyle(BaseMetadataStyle):
    @property
    def id(self) -> str:
        return "scientific_hud"

    @property
    def name(self) -> str:
        return "HUD Cient\u00edfico"

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

        self._draw_compass(draw, data, color, font_main, font_small, bg, ox, oy)
        self._draw_panels(draw, h, data, color, font_main, font_small, bg, ox)
        self._draw_scale_bar(draw, w, h, data, color, font_main, font_small, bg, ox, oy)

    def _draw_compass(self, draw, data, color, font_main, font_small, bg, ox, oy):
        cx, cy = ox + 45, oy + 55
        r = 28
        r2 = 23

        if bg:
            draw.ellipse((cx - r - 4, cy - r - 4, cx + r + 4, cy + r + 4), fill=bg)
        draw.ellipse((cx - r, cy - r, cx + r, cy + r), outline=color, width=1)
        draw.line((cx - r2, cy, cx + r2, cy), fill=color, width=1)
        draw.line((cx, cy - r2, cx, cy + r2), fill=color, width=1)

        for text, dx, dy in [("N", 0, -r - 8), ("S", 0, r + 6), ("E", r + 6, 0), ("W", -r - 10, 0)]:
            bbox = draw.textbbox((0, 0), text, font=font_small)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
            tx = cx + dx - tw // 2
            ty = cy + dy - th // 2
            if bg:
                self._text_bg(draw, tx, ty, text, font_small, bg)
            draw.text((tx, ty), text, fill=color, font=font_small)

        pole_label = "Pole (ECJ2000):"
        pole_val = data["pole"]
        lx = ox + 10
        ly = cy + r + 10
        if bg:
            self._text_bg(draw, lx, ly, pole_label, font_main, bg)
            self._text_bg(draw, lx, ly + 22, pole_val, font_small, bg)
        draw.text((lx, ly), pole_label, fill=color, font=font_main)
        draw.text((lx, ly + 22), pole_val, fill=color, font=font_small)

    def _draw_panels(self, draw, height, data, color, font_main, font_small, bg, ox):
        y_start = height - 175
        panel_w = 280

        sep_text = f"SEP (w,\u03b4):  {data['sep']}"
        ssp_text = f"SSP (\u03bb,\u00df):  {data['ssp']}"

        for i, (field_text, np_show) in enumerate([
            (sep_text, False),
            (ssp_text, False),
            (None, True)
        ]):
            y = y_start + i * 48
            px = ox + 4
            if bg:
                draw.rectangle(
                    (px, y, px + panel_w, y + 40),
                    fill=bg, outline=color, width=1,
                )
            else:
                draw.rectangle(
                    (px, y, px + panel_w, y + 40),
                    outline=color, width=1,
                )
            if np_show:
                np_val = float(data["np"])
                np_label = "NP:"
                lx = ox + 10
                if bg:
                    self._text_bg(draw, lx, y + 2, np_label, font_main, bg)
                draw.text((lx, y + 2), np_label, fill=color, font=font_main)
                bar_x, bar_y = ox + 45, y + 6
                bar_w, bar_h = 180, 14
                if bg:
                    draw.rectangle(
                        (bar_x, bar_y, bar_x + bar_w, bar_y + bar_h),
                        fill=bg, outline=color, width=1,
                    )
                else:
                    draw.rectangle(
                        (bar_x, bar_y, bar_x + bar_w, bar_y + bar_h),
                        outline=color, width=1,
                    )
                fill_w = int(bar_w * (np_val - 0.5) / 0.5)
                if fill_w > 0:
                    draw.rectangle(
                        (bar_x + 1, bar_y + 1, bar_x + fill_w - 1, bar_y + bar_h - 1),
                        fill=color,
                    )
                np_val_str = f"{np_val:.2f}"
                if bg:
                    self._text_bg(draw, bar_x + bar_w + 8, bar_y + bar_h // 2 - 4, np_val_str, font_main, bg)
                draw.text(
                    (bar_x + bar_w + 8, bar_y + bar_h // 2 - 4),
                    np_val_str, fill=color, font=font_main,
                )
            else:
                if bg:
                    self._text_bg(draw, ox + 10, y + 3, field_text, font_main, bg)
                draw.text((ox + 10, y + 3), field_text, fill=color, font=font_main)

    def _draw_scale_bar(self, draw, width, height, data, color, font_main, font_small, bg, ox, oy):
        arc_str = data["arc"]

        bar_x = ox + width - 210
        bar_y = oy + height - 35
        bar_w = 170
        bar_h = 8

        if bg:
            draw.rectangle(
                (bar_x - 6, bar_y - 22, bar_x + bar_w + 6, bar_y + bar_h + 6),
                fill=bg, outline=color, width=1,
            )

        draw.rectangle(
            (bar_x, bar_y, bar_x + bar_w, bar_y + bar_h),
            fill=None, outline=color, width=1,
        )

        mid = bar_w // 2
        draw.line((bar_x + mid, bar_y - 4, bar_x + mid, bar_y + bar_h + 4), fill=color, width=1)
        draw.line((bar_x, bar_y - 2, bar_x, bar_y + bar_h + 2), fill=color, width=1)
        draw.line((bar_x + bar_w, bar_y - 2, bar_x + bar_w, bar_y + bar_h + 2), fill=color, width=1)

        label = f"arcsecond: {arc_str}"
        bbox = draw.textbbox((0, 0), label, font=font_small)
        tw = bbox[2] - bbox[0]
        lx = bar_x + bar_w // 2 - tw // 2
        ly = bar_y - 18
        if bg:
            self._text_bg(draw, lx, ly, label, font_small, bg)
        draw.text((lx, ly), label, fill=color, font=font_small)
