from __future__ import annotations

from pathlib import Path

APP_TITLE = "📊 Генератор отчетов по курсам ПК"
BUILD_LABEL = "Build: v0.6"

PROJECT_ROOT = Path(__file__).resolve().parent.parent
METADATA_DIR = PROJECT_ROOT / "metadata"
TEMPLATES_DIR = PROJECT_ROOT / "templates"

COURSE_MAPPING_PATH = METADATA_DIR / "course_mapping.xlsx"

REGION_ORDER = [
    "Акмолинская",
    "Актюбинская",
    "Алматинская",
    "Атырауская",
    "Восточно-Казахстанская",
    "г.Алматы",
    "г.Астана",
    "г.Шымкент",
    "Жамбылская",
    "Западно-Казахстанская",
    "Карагандинская",
    "Костанайская",
    "Кызылординская",
    "Мангистауская",
    "Абай",
    "Жетісу",
    "Ұлытау",
    "Павлодарская",
    "Северо-Казахстанская",
    "Туркестанская",
]
