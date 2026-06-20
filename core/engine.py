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
        self.margin: int = 60
        self.current_style_id: str = "sepia"

    def set_font(self, path: str | None):
        self.grid_renderer.font_path = path
        self.metadata_renderer.font_path = path

    def set_canvas_size(self, size: tuple[int, int]):
        self.canvas_size = size

    def render(self, image_path: str) -> Image.Image:
        style = self.style_manager.get(self.current_style_id)
        canvas = self.image_processor.create_canvas(self.canvas_size, style.background_color)
        subject = self.image_processor.load(image_path)
        subject = self.image_processor.enhance_contrast(subject)

        data = self.data_generator.generate_all()

        inner_w = self.canvas_size[0] - 2 * self.margin
        inner_h = self.canvas_size[1] - 2 * self.margin

        subject = style.process_subject(subject)
        subject = subject.resize((inner_w, inner_h), Image.LANCZOS)

        canvas.paste(subject, (self.margin, self.margin))
        draw = ImageDraw.Draw(canvas)

        palette = style.get_palette()
        self.grid_renderer.render(
            draw=draw,
            width=self.canvas_size[0],
            height=self.canvas_size[1],
            grid_color=palette["grid"],
            text_color=palette["text"],
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

    def list_styles(self) -> list[dict]:
        return self.style_manager.list_styles()

    def set_style(self, style_id: str):
        if self.style_manager.get(style_id):
            self.current_style_id = style_id
