from app import create_app, db
from config import db_config
from dotenv import load_dotenv
import os
from sqlalchemy import inspect
from models import User  # Importer le modèle User
from werkzeug.security import generate_password_hash  # Importer generate_password_hash

load_dotenv()

# Debug
print(f"DB_HOST={os.getenv('DB_HOST')}")
print(f"DB_USER={os.getenv('DB_USER')}")
print(f"DB_PASSWORD={os.getenv('DB_PASSWORD')}")
print(f"DB_NAME={os.getenv('DB_NAME')}")
print(f"FLASK_SECRET_KEY={os.getenv('FLASK_SECRET_KEY')}")
print(f"ADMIN_PASSWORD={os.getenv('ADMIN_PASSWORD')}")

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

    # Créer un administrateur par défaut
    admin_email = 'admin@admin.com'
    if not User.query.filter_by(email=admin_email).first():
        admin_user = User(
            username='admin', 
            email=admin_email,
            password=generate_password_hash(os.getenv('ADMIN_PASSWORD'), method='pbkdf2:sha256'), 
            is_admin=True
        )
        db.session.add(admin_user)
        db.session.commit()
        print("Default admin user created successfully!")
    else:
        print("Default admin user already exists.")
