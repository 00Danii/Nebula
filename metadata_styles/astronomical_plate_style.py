from PIL import ImageDraw
from metadata_styles.base_metadata_style import BaseMetadataStyle


class AstronomicalPlateMetadataStyle(BaseMetadataStyle):
    @property
    def id(self) -> str:
        return "astronomical_plate"

    @property
    def name(self) -> str:
        return "Placa Astron\u00f3mica"

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

        self._draw_fiducials(draw, w, h, color, ox, oy)
        self._draw_frame(draw, w, h, color, ox, oy)
        self._draw_engraved_text(draw, w, h, data, color, font_main, font_small, bg, ox, oy)

    def _draw_fiducials(self, draw, width, height, color, ox, oy):
        margin = 8
        size = 8
        positions = [
            (ox + margin, oy + margin),
            (ox + width - margin, oy + margin),
            (ox + margin, oy + height - margin),
            (ox + width - margin, oy + height - margin),
        ]
        for cx, cy in positions:
            draw.line((cx - size, cy, cx + size, cy), fill=color, width=1)
            draw.line((cx, cy - size, cx, cy + size), fill=color, width=1)

    def _draw_frame(self, draw, width, height, color, ox, oy):
        draw.rectangle(
            (ox + 4, oy + 4, ox + width - 4, oy + height - 4),
            outline=color, width=1,
        )

    def _draw_engraved_text(self, draw, width, height, data, color, font_main, font_small, bg, ox, oy):
        shadow = (
            max(0, color[0] - 60),
            max(0, color[1] - 60),
            max(0, color[2] - 60),
        )

        pole_parts = data["pole"].split(", ")
        sep_parts = data["sep"].split(", ")
        ssp_parts = data["ssp"].split(", ")
        lines = [
            (f"PLT: {pole_parts[0]}", font_small),
            (pole_parts[1], font_small),
            (f"SEP: {sep_parts[0]}", font_small),
            (sep_parts[1], font_small),
            (f"SSP: {ssp_parts[0]}", font_small),
            (ssp_parts[1], font_small),
            (f"NP:  {data['np']}", font_main),
            (f"RES: {data['arc']}", font_small),
        ]

        x, y = ox + 22, oy + 22
        max_w = 0
        for text, font in lines:
            bbox = draw.textbbox((0, 0), text, font=font)
            tw = bbox[2] - bbox[0]
            if tw > max_w:
                max_w = tw
            th = bbox[3] - bbox[1]
            y += th + 6
        total_h = y - (oy + 22)
        y = oy + 22

        if bg:
            draw.rectangle(
                (x - 6, y - 6, x + max_w + 10, y + total_h + 6),
                fill=bg,
            )

        for text, font in lines:
            self._draw_with_shadow(draw, x, y, text, font, color, shadow)
            bbox = draw.textbbox((0, 0), text, font=font)
            y += (bbox[3] - bbox[1]) + 6

        corner_info = f"ECJ2000  {data['arc']}"
        bbox = draw.textbbox((0, 0), corner_info, font=font_small)
        tw = bbox[2] - bbox[0]
        ty = bbox[3] - bbox[1]
        cx = ox + width - tw - 22
        cy = oy + height - ty - 20
        if bg:
            self._text_bg(draw, cx, cy, corner_info, font_small, bg, pad_x=6, pad_y=4)
        self._draw_with_shadow(draw, cx, cy, corner_info, font_small, color, shadow)

    def _draw_with_shadow(self, draw, x, y, text, font, color, shadow):
        draw.text((x + 1, y + 1), text, fill=shadow, font=font)
        draw.text((x, y), text, fill=color, font=font)
