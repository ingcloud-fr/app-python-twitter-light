# initialize_db.py

import time
import mysql.connector
from app import db, app

def wait_for_db():
    while True:
        try:
            conn = mysql.connector.connect(
                host=app.config['SQLALCHEMY_DATABASE_URI'].split('@')[1].split('/')[0].split(':')[0],
                user=app.config['SQLALCHEMY_DATABASE_URI'].split('//')[1].split(':')[0],
                password=app.config['SQLALCHEMY_DATABASE_URI'].split(':')[2].split('@')[0]
            )
            conn.close()
            break
        except mysql.connector.Error as err:
            print("Waiting for MySQL to be ready...")
            time.sleep(5)

wait_for_db()

with app.app_context():
    db.create_all()

