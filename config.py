# config.py
import os
from dotenv import load_dotenv

# Charger les variables d'environnement à partir du fichier .env
load_dotenv()

db_config = {
    'user': os.getenv('DB_USER', 'default_user'),
    'password': os.getenv('DB_PASSWORD', 'default_password'),
    'host': os.getenv('DB_HOST', 'localhost'),
    'database': os.getenv('DB_NAME', 'default_db_name')
}

SECRET_KEY = os.getenv('SECRET_KEY', 'your_secret_key')


# # Debugging print statements
# print(f"DB_HOST={db_config['host']}")
# print(f"DB_USER={db_config['user']}")
# print(f"DB_PASSWORD={db_config['password']}")
# print(f"DB_NAME={db_config['database']}")
# print(f"SECRET_KEY={SECRET_KEY}")