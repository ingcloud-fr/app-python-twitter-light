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
    
    # Check if tables exist
    inspector = inspect(db.engine)
    table_names = inspector.get_table_names()
    
    if 'user' not in table_names or 'article' not in table_names:
        db.create_all()
        print("Tables created successfully!")
    else:
        print("Tables already exist. No need to create them.")