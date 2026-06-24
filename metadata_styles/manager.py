from metadata_styles.base_metadata_style import BaseMetadataStyle
from metadata_styles.minimal_style import MinimalMetadataStyle
from metadata_styles.scientific_hud_style import ScientificHUDMetadataStyle
from metadata_styles.astronomical_plate_style import AstronomicalPlateMetadataStyle
from metadata_styles.geometric_style import GeometricMetadataStyle
from metadata_styles.alien_hud_style import AlienHUDMetadataStyle


class MetadataStyleManager:
    def __init__(self):
        self._styles: dict[str, BaseMetadataStyle] = {}
        self._register_defaults()

    def _register_defaults(self):
        self.register(AlienHUDMetadataStyle())
        self.register(MinimalMetadataStyle())
        self.register(ScientificHUDMetadataStyle())
        self.register(AstronomicalPlateMetadataStyle())
        self.register(GeometricMetadataStyle())

    def register(self, style: BaseMetadataStyle):
        self._styles[style.id] = style

    def get(self, style_id: str) -> BaseMetadataStyle | None:
        return self._styles.get(style_id)

    def list_styles(self) -> list[dict]:
        return [
            {"id": sid, "name": s.name}
            for sid, s in self._styles.items()
        ]
