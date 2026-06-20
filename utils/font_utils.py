from PIL import ImageFont


class FontManager:
    _instance = None
    _fonts: dict[str, ImageFont.FreeTypeFont | ImageFont.ImageFont] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def load(self, path: str | None, size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
        cache_key = f"{path}_{size}"
        if cache_key in self._fonts:
            return self._fonts[cache_key]

        font = self._try_load(path, size)
        self._fonts[cache_key] = font
        return font

    def _try_load(self, path: str | None, size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
        if path:
            try:
                return ImageFont.truetype(path, size)
            except (IOError, OSError):
                pass
        fallback_paths = ["consola.ttf", "consolab.ttf", "cour.ttf", "courbd.ttf",
                          "DejaVuSansMono.ttf", "LiberationMono-Regular.ttf",
                          "CascadiaMono.ttf", "CascadiaCode.ttf"]
        for fp in fallback_paths:
            try:
                return ImageFont.truetype(fp, size)
            except (IOError, OSError):
                continue
        try:
            return ImageFont.truetype("arial.ttf", size)
        except (IOError, OSError):
            return ImageFont.load_default()

    def clear_cache(self):
        self._fonts.clear()
