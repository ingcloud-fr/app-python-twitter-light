from app import create_app, db
from config import db_config
from dotenv import load_dotenv
import os

load_dotenv()

# Debug
# print(f"DB_HOST={os.getenv('DB_HOST')}")
# print(f"DB_USER={os.getenv('DB_USER')}")
# print(f"DB_PASSWORD={os.getenv('DB_PASSWORD')}")
# print(f"DB_NAME={os.getenv('DB_NAME')}")
# print(f"SECRET_KEY={os.getenv('SECRET_KEY')}")

app = create_app()

with app.app_context():
    print(f"DB Config: {db_config}")
    db.create_all()
    print("Toutes les tables ont été créées avec succès!")
