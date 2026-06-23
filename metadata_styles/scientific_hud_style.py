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
        w = self._img_w(image_rect, width) if image_rect is not None else width
        h = self._img_h(image_rect, height) if image_rect is not None else height
        ox, oy = self._img_offset(image_rect, 0, 0) if image_rect is not None else (0, 0)
        bg = self._blend_bg(bg_color) if bg_color else None

        self._draw_compass(draw, data, color, font_main, font_small, bg, ox, oy, inside)
        self._draw_panels(draw, h, data, color, font_main, font_small, bg, ox, oy, inside)
        self._draw_scale_bar(draw, w, h, data, color, font_main, font_small, bg, ox, oy, inside)

    def _draw_compass(self, draw, data, color, font_main, font_small, bg, ox, oy, inside):
        b_pole_label = draw.textbbox((0, 0), "Pole (ECJ2000):", font=font_main)
        b_pole_val = draw.textbbox((0, 0), data["pole"], font=font_small)
        pole_th = b_pole_val[3] - b_pole_val[1]
        group_h = 111 + pole_th

        x = ox + 22
        y = oy + (12 if inside else -group_h - 12)
        cx, cy = x + 30, y + 30
        r = 28

        pole_label = "Pole (ECJ2000):"
        pole_val = data["pole"]
        lx = x
        ly = cy + r + 8

        text_w = max(b_pole_label[2] - b_pole_label[0], b_pole_val[2] - b_pole_val[0])
        pole_th = b_pole_val[3] - b_pole_val[1]

        if bg:
            group_x = min(cx - r, lx) - 20
            group_y = min(cy - r, y) - 10
            group_w = max(cx + r, lx + text_w) - group_x + 12
            group_h_dyn = max(cy + r, ly + 22 + pole_th) - group_y + 8 + 15
            draw.rectangle((group_x, group_y, group_x + group_w, group_y + group_h_dyn), fill=bg)


        draw.ellipse((cx - r, cy - r, cx + r, cy + r), outline=color, width=1)
        draw.line((cx - r + 5, cy, cx + r - 5, cy), fill=color, width=1)
        draw.line((cx, cy - r + 5, cx, cy + r - 5), fill=color, width=1)

        for text, dx, dy in [("N", 0, -r - 6), ("S", 0, r + 4), ("E", r + 4, 0), ("W", -r - 8, 0)]:
            b = draw.textbbox((0, 0), text, font=font_small)
            tw = b[2] - b[0]
            th = b[3] - b[1]
            draw.text((cx + dx - tw // 2, cy + dy - th // 2), text, fill=color, font=font_small)

        draw.text((lx, ly + 10), pole_label, fill=color, font=font_main)
        draw.text((lx, ly + 32), pole_val, fill=color, font=font_small)

    def _draw_panels(self, draw, height, data, color, font_main, font_small, bg, ox, oy, inside):
        x = ox + 6
        sep_text = f"SEP (w,\u03b4):  {data['sep']}"
        ssp_text = f"SSP (\u03bb,\u00df):  {data['ssp']}"
        np_val = float(data["np"])
        np_val_str = f"{np_val:.2f}"

        b_sep = draw.textbbox((0, 0), sep_text, font=font_main)
        b_np_label = draw.textbbox((0, 0), "NP:", font=font_main)
        b_np_val = draw.textbbox((0, 0), np_val_str, font=font_main)
        line_h = b_sep[3] - b_sep[1]
        panel_h = line_h + 20
        spacing = 6

        sep_text_w = b_sep[2] - b_sep[0]
        b_ssp = draw.textbbox((0, 0), ssp_text, font=font_main)
        ssp_text_w = b_ssp[2] - b_ssp[0]
        np_label_w = b_np_label[2] - b_np_label[0]
        np_val_w = b_np_val[2] - b_np_val[0]
        bar_w = max(140, int(sep_text_w * 0.6))
        np_total_w = 8 + np_label_w + 8 + bar_w + 8 + np_val_w + 8
        panel_w = max(sep_text_w, ssp_text_w, np_total_w) + 16

        sep_y = 0
        ssp_y = panel_h + spacing
        np_y = 2 * (panel_h + spacing)

        total_h = np_y + panel_h
        y_offset = oy + (height - total_h - 6 if inside else height + 10)

        if bg:
            draw.rectangle(
                (x - 4, y_offset + sep_y - 4, x + panel_w + 4, y_offset + np_y + panel_h + 4),
                fill=bg,
            )

        draw.rectangle((x, y_offset + sep_y, x + panel_w, y_offset + sep_y + panel_h), outline=color, width=1)
        draw.text((x + 8, y_offset + sep_y + 4), sep_text, fill=color, font=font_main)

        draw.rectangle((x, y_offset + ssp_y, x + panel_w, y_offset + ssp_y + panel_h), outline=color, width=1)
        draw.text((x + 8, y_offset + ssp_y + 4), ssp_text, fill=color, font=font_main)

        draw.rectangle((x, y_offset + np_y, x + panel_w, y_offset + np_y + panel_h), outline=color, width=1)
        draw.text((x + 8, y_offset + np_y + 4), "NP:", fill=color, font=font_main)

        bar_x = x + 8 + np_label_w + 8
        bar_y = y_offset + np_y + 7
        bar_h = max(10, line_h)
        draw.rectangle((bar_x, bar_y, bar_x + bar_w, bar_y + bar_h), outline=color, width=1)
        fill_w = int(bar_w * (np_val - 0.5) / 0.5)
        if fill_w > 0:
            draw.rectangle((bar_x + 1, bar_y + 1, bar_x + fill_w - 1, bar_y + bar_h - 1), fill=color)
        draw.text((bar_x + bar_w + 8, bar_y + bar_h // 2 - line_h // 2), np_val_str, fill=color, font=font_main)

    def _draw_scale_bar(self, draw, width, height, data, color, font_main, font_small, bg, ox, oy, inside):
        arc_str = data["arc"]
        label = f"arcsecond: {arc_str}"
        bbox = draw.textbbox((0, 0), label, font=font_small)
        tw = bbox[2] - bbox[0]

        bar_w = 170
        bar_h = 8
        pad_right = 8 if inside else 10
        bar_x = ox + width - bar_w - pad_right
        bar_y = oy + (height - 14 if inside else height + 10)
        lx = bar_x + bar_w // 2 - tw // 2
        ly = bar_y - 18

        if bg:
            bx = min(bar_x, lx) - 6
            by = ly - 4
            bw = max(bar_x + bar_w, lx + tw) - bx + 6
            bh = (bar_y + bar_h + 4) - by
            draw.rectangle((bx, by, bx + bw, by + bh), fill=bg)

        draw.rectangle((bar_x, bar_y, bar_x + bar_w, bar_y + bar_h), fill=None, outline=color, width=1)
        mid = bar_w // 2
        draw.line((bar_x + mid, bar_y - 4, bar_x + mid, bar_y + bar_h + 4), fill=color, width=1)
        draw.line((bar_x, bar_y - 2, bar_x, bar_y + bar_h + 2), fill=color, width=1)
        draw.line((bar_x + bar_w, bar_y - 2, bar_x + bar_w, bar_y + bar_h + 2), fill=color, width=1)
        draw.text((lx, ly), label, fill=color, font=font_small)
