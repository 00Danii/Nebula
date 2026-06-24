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
        bg = self._blend_bg(bg_color) if bg_color else None

        if inside:
            w = self._img_w(image_rect, width)
            h = self._img_h(image_rect, height)
            ox, oy = self._img_offset(image_rect, 0, 0)
            self._draw_compass(draw, data, color, font_main, font_small, bg, ox, oy, True)
            self._draw_panels(draw, h, data, color, font_main, font_small, bg, ox, oy, True)
            self._draw_scale_bar(draw, w, h, data, color, font_main, font_small, bg, ox, oy, True)
        elif image_rect is not None and image_rect[2] < image_rect[3]:
            self._draw_outside_portrait(draw, width, height, data, color, font_main, font_small, bg, image_rect)
        else:
            self._draw_compass(draw, data, color, font_main, font_small, bg, 0, 0, False)
            self._draw_panels(draw, height, data, color, font_main, font_small, bg, 0, 0, False)
            self._draw_scale_bar(draw, width, height, data, color, font_main, font_small, bg, 0, 0, False)

    def _draw_outside_portrait(self, draw, width, height, data, color, font_main, font_small, bg, image_rect):
        offset_x, offset_y, disp_w, disp_h = image_rect
        x_left = 30
        pole_parts = data["pole"].split(", ")
        sep_parts = data["sep"].split(", ")
        ssp_parts = data["ssp"].split(", ")

        line1 = "Pole (ECJ2000):"
        b_pole_label = draw.textbbox((0, 0), line1, font=font_main)
        b_r1 = draw.textbbox((0, 0), pole_parts[0], font=font_small)
        b_r2 = draw.textbbox((0, 0), pole_parts[1], font=font_small)
        text_w_pole = max(b_pole_label[2] - b_pole_label[0], b_r1[2] - b_r1[0], b_r2[2] - b_r2[0])
        line_h = b_pole_label[3] - b_pole_label[1]
        small_h = b_r1[3] - b_r1[1]

        x, y = x_left, 30
        cx, cy = x + 30, y + 30
        r = 28
        lx = x
        ly = cy + r + 8

        if bg:
            group_x = min(cx - r, lx) - 20
            group_y = min(cy - r, y) - 10
            group_w = max(cx + r, lx + text_w_pole) - group_x + 12
            group_h = max(cy + r, ly + 10 + 22 + 22 + small_h) - group_y + 8 + 15
            draw.rectangle((group_x, group_y, group_x + group_w, group_y + group_h), fill=bg)

        draw.ellipse((cx - r, cy - r, cx + r, cy + r), outline=color, width=1)
        draw.line((cx - r + 5, cy, cx + r - 5, cy), fill=color, width=1)
        draw.line((cx, cy - r + 5, cx, cy + r - 5), fill=color, width=1)
        for text, dx, dy in [("N", 0, -r - 6), ("S", 0, r + 4), ("E", r + 4, 0), ("W", -r - 8, 0)]:
            b = draw.textbbox((0, 0), text, font=font_small)
            tw, th = b[2] - b[0], b[3] - b[1]
            draw.text((cx + dx - tw // 2, cy + dy - th // 2), text, fill=color, font=font_small)
        draw.text((lx, ly + 10), line1, fill=color, font=font_main)
        draw.text((lx, ly + 32), pole_parts[0], fill=color, font=font_small)
        draw.text((lx, ly + 54), pole_parts[1], fill=color, font=font_small)

        sep_lines = [
            ("SEP (w,\u03b4):", font_main),
            (sep_parts[0], font_small),
            (sep_parts[1], font_small),
        ]
        ssp_lines = [
            ("SSP (\u03bb,\u00df):", font_main),
            (ssp_parts[0], font_small),
            (ssp_parts[1], font_small),
        ]
        np_val = float(data["np"])
        np_val_str = f"{np_val:.2f}"
        b_np_label = draw.textbbox((0, 0), "NP:", font=font_main)
        b_np_val = draw.textbbox((0, 0), np_val_str, font=font_main)
        np_label_w = b_np_label[2] - b_np_label[0]
        np_val_w = b_np_val[2] - b_np_val[0]

        sep_panel_h = 8 + line_h + 4 + small_h + 2 + small_h + 4
        ssp_panel_h = sep_panel_h
        spacing = 6
        sep_y_pos = 0
        ssp_y_pos = sep_panel_h + spacing
        np_panel_h = line_h + 20
        np_y_pos = ssp_y_pos + ssp_panel_h + spacing
        total_panel_h = np_y_pos + np_panel_h

        sep_w = max(draw.textbbox((0, 0), t, font=f)[2] - draw.textbbox((0, 0), t, font=f)[0] for t, f in sep_lines)
        ssp_w = max(draw.textbbox((0, 0), t, font=f)[2] - draw.textbbox((0, 0), t, font=f)[0] for t, f in ssp_lines)
        bar_w = max(100, int(max(sep_w, ssp_w) * 0.5))
        np_total_w = 8 + np_label_w + 8 + bar_w + 8 + np_val_w + 8
        panel_w = min(max(sep_w, ssp_w, np_total_w) + 16, max(offset_x - x_left, 160))

        compass_end = ly + 54 + small_h + 15
        y_offset = height - total_panel_h - 10
        if y_offset < compass_end + 15:
            y_offset = compass_end + 15

        x = x_left
        if bg:
            draw.rectangle(
                (x - 4, y_offset + sep_y_pos - 4, x + panel_w + 4, y_offset + np_y_pos + np_panel_h + 4),
                fill=bg,
            )

        draw.rectangle((x, y_offset + sep_y_pos, x + panel_w, y_offset + sep_y_pos + sep_panel_h), outline=color, width=1)
        draw.text((x + 8, y_offset + sep_y_pos + 4), "SEP (w,\u03b4):", fill=color, font=font_main)
        draw.text((x + 8, y_offset + sep_y_pos + 4 + line_h + 4), sep_parts[0], fill=color, font=font_small)
        draw.text((x + 8, y_offset + sep_y_pos + 4 + line_h + 4 + small_h + 2), sep_parts[1], fill=color, font=font_small)

        draw.rectangle((x, y_offset + ssp_y_pos, x + panel_w, y_offset + ssp_y_pos + ssp_panel_h), outline=color, width=1)
        draw.text((x + 8, y_offset + ssp_y_pos + 4), "SSP (\u03bb,\u00df):", fill=color, font=font_main)
        draw.text((x + 8, y_offset + ssp_y_pos + 4 + line_h + 4), ssp_parts[0], fill=color, font=font_small)
        draw.text((x + 8, y_offset + ssp_y_pos + 4 + line_h + 4 + small_h + 2), ssp_parts[1], fill=color, font=font_small)

        np_panel_y = y_offset + np_y_pos
        draw.rectangle((x, np_panel_y, x + panel_w, np_panel_y + np_panel_h), outline=color, width=1)
        draw.text((x + 8, np_panel_y + 4), "NP:", fill=color, font=font_main)
        bar_x = x + 8 + np_label_w + 8
        bar_y = np_panel_y + 7
        bar_h = max(10, line_h)
        draw.rectangle((bar_x, bar_y, bar_x + bar_w, bar_y + bar_h), outline=color, width=1)
        fill_w = int(bar_w * min(max((np_val - 0.5) / 0.5, 0), 1))
        if fill_w > 0:
            draw.rectangle((bar_x + 1, bar_y + 1, bar_x + fill_w - 1, bar_y + bar_h - 1), fill=color)
        draw.text((bar_x + bar_w + 8, bar_y + bar_h // 2 - line_h // 2), np_val_str, fill=color, font=font_main)

        arc_str = data["arc"]
        label = f"arcsecond: {arc_str}"
        bbox = draw.textbbox((0, 0), label, font=font_small)
        tw = bbox[2] - bbox[0]
        bar_w_r = 170
        bar_h_r = 8
        bar_x_r = width - bar_w_r - 30
        bar_y_r = height - 30
        lx_r = bar_x_r + bar_w_r // 2 - tw // 2
        ly_r = bar_y_r - 18
        if bg:
            bx = min(bar_x_r, lx_r) - 6
            by = ly_r - 4
            bw = max(bar_x_r + bar_w_r, lx_r + tw) - bx + 6
            bh = (bar_y_r + bar_h_r + 4) - by
            draw.rectangle((bx, by, bx + bw, by + bh), fill=bg)
        draw.rectangle((bar_x_r, bar_y_r, bar_x_r + bar_w_r, bar_y_r + bar_h_r), fill=None, outline=color, width=1)
        mid = bar_w_r // 2
        draw.line((bar_x_r + mid, bar_y_r - 4, bar_x_r + mid, bar_y_r + bar_h_r + 4), fill=color, width=1)
        draw.line((bar_x_r, bar_y_r - 2, bar_x_r, bar_y_r + bar_h_r + 2), fill=color, width=1)
        draw.line((bar_x_r + bar_w_r, bar_y_r - 2, bar_x_r + bar_w_r, bar_y_r + bar_h_r + 2), fill=color, width=1)
        draw.text((lx_r, ly_r), label, fill=color, font=font_small)

    def _draw_compass(self, draw, data, color, font_main, font_small, bg, ox, oy, inside):
        x, y = ox + (22 if inside else 30), oy + (12 if inside else 30)
        cx, cy = x + 30, y + 30
        r = 28

        pole_label = "Pole (ECJ2000):"
        pole_val = data["pole"]
        lx = x
        ly = cy + r + 8

        b_pole_label = draw.textbbox((0, 0), pole_label, font=font_main)
        b_pole_val = draw.textbbox((0, 0), pole_val, font=font_small)
        text_w = max(b_pole_label[2] - b_pole_label[0], b_pole_val[2] - b_pole_val[0])
        pole_th = b_pole_val[3] - b_pole_val[1]

        if bg:
            group_x = min(cx - r, lx) - 20
            group_y = min(cy - r, y) - 10
            group_w = max(cx + r, lx + text_w) - group_x + 12
            group_h = max(cy + r, ly + 22 + pole_th) - group_y + 8 + 15
            draw.rectangle((group_x, group_y, group_x + group_w, group_y + group_h), fill=bg)

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
        x = ox + (6 if inside else 30)
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
        y_offset = oy + height - total_h - (6 if inside else 10)

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
        bar_y = oy + height - (14 if inside else 30)
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
