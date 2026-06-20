import cv2
import numpy as np
from PIL import Image


class ImageProcessor:
    def load(self, path: str) -> Image.Image:
        img = cv2.imread(path)
        if img is None:
            raise FileNotFoundError(f"No se pudo cargar la imagen: {path}")
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        return Image.fromarray(img_rgb)

    def enhance_contrast(self, image: Image.Image, clip_limit: float = 2.0, grid_size: int = 8) -> Image.Image:
        img_array = np.array(image.convert("L"), dtype=np.uint8)
        clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(grid_size, grid_size))
        enhanced = clahe.apply(img_array)
        return Image.fromarray(enhanced).convert("RGB")

    def to_grayscale(self, image: Image.Image) -> Image.Image:
        return image.convert("L").convert("RGB")

    def resize_to_fit(self, image: Image.Image, max_size: tuple[int, int]) -> Image.Image:
        image.thumbnail(max_size, Image.LANCZOS)
        return image

    def create_canvas(self, size: tuple[int, int], background: tuple[int, int, int] = (0, 0, 0)) -> Image.Image:
        return Image.new("RGB", size, background)
