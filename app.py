import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler
import re
from models import db, User, Article
from config import db_config, SECRET_KEY

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+mysqlconnector://{db_config['user']}:{db_config['password']}@{db_config['host']}/{db_config['database']}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = SECRET_KEY

    # Configurer l'upload d'images
    UPLOAD_FOLDER = 'static/uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    db.init_app(app)

    if not app.debug:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/lwitter.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('Lwitter startup')

        # Ajouter un file handler pour le health check curl
        curl_log_handler = RotatingFileHandler('/var/log/curl_health_check.log', maxBytes=10240, backupCount=10)
        curl_log_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s'
        ))
        curl_log_handler.setLevel(logging.INFO)
        app.logger.addHandler(curl_log_handler)

    return app

app = create_app()

@app.route('/health')
def health_check():
    app.logger.info("Health check endpoint was hit!")
    return 'OK', 200

@app.route('/health2')
def health_check2():
    app.logger.info("Health check endpoint 2 was hit!")
    return 'OK', 200

# Route de test supplémentaire pour vérifier la connectivité
@app.route('/test')
def test_connectivity():
    app.logger.info("Test connectivity endpoint was hit!")
    return 'Connectivity OK', 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
