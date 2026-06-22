from PIL import Image, ImageDraw
import numpy as np
import copy

from core.image_processor import ImageProcessor
from core.grid_renderer import GridRenderer
from core.metadata_renderer import MetadataRenderer
from core.data_generator import DataGenerator
from styles.style_manager import StyleManager
from utils.font_utils import FontManager


class RenderEngine:
    def __init__(self):
        self.image_processor = ImageProcessor()
        self.grid_renderer = GridRenderer()
        self.metadata_renderer = MetadataRenderer()
        self.data_generator = DataGenerator()
        self.style_manager = StyleManager()
        self.font_manager = FontManager()

        self.canvas_size: tuple[int, int] = (1024, 1024)
        self.margin: int = 80
        self.current_style_id: str = "sepia"
        self._original_image: Image.Image | None = None

        self._adjustments: dict[str, float] = {
            "brightness": 0,
            "contrast": 0,
            "saturation": 0,
            "hue": 0,
            "sharpness": 0,
            "gamma": 1.0,
            "temperature": 0,
            "vibrance": 0,
            "exposure": 0,
        }

        self._display_config: dict = {
            "font_size_main": 14,
            "font_size_small": 11,
            "meta_font_size": 16,
            "font_name": "Consola",
            "grid_num_lines": 10,
            "grid_line_width": 1,
            "grid_show_on_image": False,
            "show_metadata": True,
        }

        self._history: list[dict] = []
        self._history_idx: int = -1
        self._max_history: int = 50
        self._save_state()

    def _save_state(self):
        styles = self.style_manager
        snapshot = {
            "adjustments": copy.deepcopy(self._adjustments),
            "display_config": copy.deepcopy(self._display_config),
            "current_style_id": self.current_style_id,
            "style_params": {
                sid: styles.get(sid).get_style_params() if styles.get(sid) else {}
                for sid in ["sepia","crt","thermal","noir","cyberpunk","vaporwave",
                            "gold","ice","pastel","muted","invert","neon","duotone",
                            "tritone","custom"]
            },
            "style_colors": {
                sid: styles.get(sid).get_editable_colors() if styles.get(sid) else {}
                for sid in ["sepia","crt","thermal","noir","cyberpunk","vaporwave",
                            "gold","ice","pastel","muted","invert","neon","duotone",
                            "tritone","custom"]
            },
        }
        if self._history_idx < len(self._history) - 1:
            self._history = self._history[:self._history_idx + 1]
        self._history.append(snapshot)
        if len(self._history) > self._max_history:
            self._history.pop(0)
        self._history_idx = len(self._history) - 1

    def _restore_state(self, snapshot: dict):
        self._adjustments = copy.deepcopy(snapshot["adjustments"])
        self._display_config = copy.deepcopy(snapshot["display_config"])
        self.current_style_id = snapshot["current_style_id"]
        for sid, params in snapshot["style_params"].items():
            style = self.style_manager.get(sid)
            if not style:
                continue
            self.style_manager.reset_style(sid)
            style = self.style_manager.get(sid)
            for pname, pdef in params.items():
                style.update_style_param(pname, pdef.get("value"))
        for sid, colors in snapshot["style_colors"].items():
            style = self.style_manager.get(sid)
            if not style:
                continue
            for ckey, cval in colors.items():
                style.update_color(ckey, cval)

    def undo(self):
        if self._history_idx > 0:
            self._history_idx -= 1
            self._restore_state(self._history[self._history_idx])

    def redo(self):
        if self._history_idx < len(self._history) - 1:
            self._history_idx += 1
            self._restore_state(self._history[self._history_idx])

    FONT_MAP: dict[str, str | None] = {
        "Consola": "consola.ttf",
        "Courier New": "cour.ttf",
        "Arial": "arial.ttf",
        "DejaVu Sans Mono": "DejaVuSansMono.ttf",
        "Cascadia Code": "CascadiaCode.ttf",
        "Defecto": None,
    }

    def set_font(self, path: str | None):
        self.grid_renderer.font_path = path
        self.metadata_renderer.font_path = path

    def set_canvas_size(self, size: tuple[int, int]):
        self.canvas_size = size

    @property
    def display_config(self) -> dict:
        return dict(self._display_config)

    def set_display_config(self, key: str, value):
        if key in self._display_config:
            if key in ("show_metadata", "grid_show_on_image"):
                value = value == "Si" if isinstance(value, str) else bool(value)
            self._display_config[key] = value
        self._save_state()

    @property
    def original_image(self) -> Image.Image | None:
        return self._original_image

    @property
    def adjustments(self) -> dict[str, float]:
        return dict(self._adjustments)

    def set_adjustment(self, key: str, value: float):
        if key in self._adjustments:
            self._adjustments[key] = value
        self._save_state()

    def reset_adjustments(self):
        self._adjustments["brightness"] = 0
        self._adjustments["contrast"] = 0
        self._adjustments["saturation"] = 0
        self._adjustments["hue"] = 0
        self._adjustments["sharpness"] = 0
        self._adjustments["gamma"] = 1.0
        self._adjustments["temperature"] = 0
        self._adjustments["vibrance"] = 0
        self._adjustments["exposure"] = 0
        self._save_state()

    def render(self, image_path: str) -> Image.Image:
        style = self.style_manager.get(self.current_style_id)
        canvas = self.image_processor.create_canvas(self.canvas_size, (0, 0, 0))

        subject_original = self.image_processor.load(image_path)
        self._original_image = subject_original.copy()

        subject = self.image_processor.enhance_contrast(subject_original)
        subject = self.image_processor.apply_adjustments(subject, self._adjustments)

        arr = np.array(subject.convert("RGB"), dtype=np.float32)
        mean_rgb = (arr[:,:,0].mean(), arr[:,:,1].mean(), arr[:,:,2].mean())
        gray = np.mean(arr, axis=2)
        mean_l = gray.mean()
        std_l = gray.std()

        data = self.data_generator.generate_all(
            img_w=subject.size[0], img_h=subject.size[1],
            mean_rgb=mean_rgb, mean_l=mean_l, std_l=std_l,
            adjustments=self._adjustments,
            style_id=self.current_style_id,
        )

        inner_w = self.canvas_size[0] - 2 * self.margin
        inner_h = self.canvas_size[1] - 2 * self.margin

        img_w, img_h = subject.size
        ratio = min(inner_w / img_w, inner_h / img_h)
        disp_w = int(img_w * ratio)
        disp_h = int(img_h * ratio)
        offset_x = self.margin + (inner_w - disp_w) // 2
        offset_y = self.margin + (inner_h - disp_h) // 2

        subject = style.process_subject(subject)
        subject_resized = subject.resize((disp_w, disp_h), Image.LANCZOS)
        canvas.paste(subject_resized, (offset_x, offset_y))

        draw = ImageDraw.Draw(canvas)
        palette = style.get_palette()

        dc = self._display_config

        font_path = self.FONT_MAP.get(dc["font_name"], None)
        self.grid_renderer.font_path = font_path
        self.metadata_renderer.font_path = font_path

        self.grid_renderer.font_size_main = dc["font_size_main"]
        self.grid_renderer.font_size_small = dc["font_size_small"]
        self.grid_renderer.num_lines = dc["grid_num_lines"]
        self.grid_renderer.line_width = dc["grid_line_width"]
        self.grid_renderer.show_on_image = dc["grid_show_on_image"]

        self.metadata_renderer.font_size_main = dc["meta_font_size"]

        image_rect = (offset_x, offset_y, disp_w, disp_h)
        self.grid_renderer.render(
            draw=draw,
            width=self.canvas_size[0],
            height=self.canvas_size[1],
            grid_color=palette["grid"],
            text_color=palette["text"],
            image_rect=image_rect,
        )
        if dc["show_metadata"]:
            self.metadata_renderer.render(
                draw=draw,
                width=self.canvas_size[0],
                height=self.canvas_size[1],
                data=data,
                color=palette["text"],
            )
        style.apply_post_effects(canvas, draw, self.canvas_size)
        return canvas

    def update_style_param(self, param_name: str, value):
        self.style_manager.update_style_param(self.current_style_id, param_name, value)
        self._save_state()

    def update_style_color(self, color_key: str, value: tuple[int, int, int]):
        self.style_manager.update_style_color(self.current_style_id, color_key, value)
        self._save_state()

    def list_styles(self) -> list[dict]:
        return self.style_manager.list_styles()

    def set_style(self, style_id: str):
        if self.style_manager.get(style_id):
            self.current_style_id = style_id
        self._save_state()

    def reset_style(self):
        self.style_manager.reset_style(self.current_style_id)
        self._save_state()
        self.set_style(self.current_style_id)
