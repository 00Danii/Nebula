from PIL import Image, ImageDraw

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

    def set_font(self, path: str | None):
        self.grid_renderer.font_path = path
        self.metadata_renderer.font_path = path

    def set_canvas_size(self, size: tuple[int, int]):
        self.canvas_size = size

    @property
    def original_image(self) -> Image.Image | None:
        return self._original_image

    @property
    def adjustments(self) -> dict[str, float]:
        return dict(self._adjustments)

    def set_adjustment(self, key: str, value: float):
        if key in self._adjustments:
            self._adjustments[key] = value

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

    def render(self, image_path: str) -> Image.Image:
        style = self.style_manager.get(self.current_style_id)
        canvas = self.image_processor.create_canvas(self.canvas_size, (0, 0, 0))

        subject_original = self.image_processor.load(image_path)
        self._original_image = subject_original.copy()

        subject = self.image_processor.enhance_contrast(subject_original)
        subject = self.image_processor.apply_adjustments(subject, self._adjustments)

        data = self.data_generator.generate_all()

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

        self.grid_renderer.render(
            draw=draw,
            width=self.canvas_size[0],
            height=self.canvas_size[1],
            grid_color=palette["grid"],
            text_color=palette["text"],
            image_rect=(offset_x, offset_y, disp_w, disp_h),
        )
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

    def list_styles(self) -> list[dict]:
        return self.style_manager.list_styles()

    def set_style(self, style_id: str):
        if self.style_manager.get(style_id):
            self.current_style_id = style_id
