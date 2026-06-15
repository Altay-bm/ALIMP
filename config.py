from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATABASE_URL = f"sqlite:///{BASE_DIR / 'alimp.db'}"
SECRET_KEY = "change-this-secret-key"

# Equipment catalog
EQUIPMENT_CATALOG = [
    ("АЛИМП-01", "Защита ЛЭП 6-35 кВ"),
    ("ВОМП-01", "Волновое определение места повреждения"),
    ("ИМЗ ОЗЗ", "Индивидуальная защита от замыканий на землю"),
]
