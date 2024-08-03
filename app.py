# app.py

from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import re
from models import db, User, Article
from config import db_config, SECRET_KEY
import logging
from logging.handlers import RotatingFileHandler

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+mysqlconnector://{db_config['user']}:{db_config['password']}@{db_config['host']}/{db_config['database']}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = SECRET_KEY

    # Configurer l'upload d'images
    UPLOAD_FOLDER = 'static/uploads'
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

    return app

app = create_app()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.before_request
def log_request_info():
    app.logger.info('Request Headers: %s', request.headers)
    app.logger.info('Request Body: %s', request.get_data())

@app.route('/')
def home():
    category = request.args.get('category')
    if category:
        articles = Article.query.filter_by(category=category).order_by(Article.created_at.desc()).all()
    else:
        articles = Article.query.order_by(Article.created_at.desc()).all()
    return render_template('home.html', articles=articles)

@app.route('/article/<int:article_id>')
def article(article_id):
    article = Article.query.get_or_404(article_id)
    return render_template('article.html', article=article)

@app.route('/article/delete/<int:article_id>', methods=['POST'])
def delete_article(article_id):
    article = Article.query.get_or_404(article_id)
    if article.author_id != session.get('user_id'):
        flash('Vous ne pouvez supprimer que vos propres articles.')
        return redirect(url_for('home'))
    db.session.delete(article)
    db.session.commit()
    flash('Article supprimé avec succès.')
    return redirect(url_for('home'))

@app.route('/article/edit/<int:article_id>', methods=['GET', 'POST'])
def edit_article(article_id):
    article = Article.query.get_or_404(article_id)
    if article.author_id != session.get('user_id'):
        flash('Vous ne pouvez modifier que vos propres articles.')
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        title = request.form['title']
        category = request.form['category']
        content = request.form['content']
        file = request.files['image']
        
        if not title or not category or not content:
            flash('Tous les champs sont obligatoires.')
        elif len(content.split()) > 1000:
            flash('Le contenu dépasse la limite maximale de 1000 mots.')
        elif file and allowed_file(file.filename):
            if file.mimetype not in ['image/jpeg', 'image/png', 'image/gif']:
                flash('Format d\'image non supporté.')
            elif len(file.read()) > 1 * 1024 * 1024:  # 1 Mo
                flash('La taille de l\'image dépasse 1 Mo.')
            else:
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.seek(0)
                file.save(filepath)
                article.image_path = filepath
        article.title = title
        article.category = category
        article.content = content
        article.updated_at = datetime.utcnow()
        
        db.session.commit()
        flash('Article modifié avec succès !')
        return redirect(url_for('article', article_id=article.id))
    
    return render_template('edit_article.html', article=article)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash('Adresse email invalide.')
            return redirect(url_for('register'))
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Inscription réussie ! Veuillez vous connecter.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Connexion réussie !')
            return redirect(url_for('home'))
        else:
            flash('Identifiants invalides. Veuillez réessayer.')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    flash('Vous avez été déconnecté.')
    return redirect(url_for('home'))

@app.route('/health')
def health_check():
    app.logger.info('Health check endpoint was hit !')
    return 'OK', 200

@app.route('/write', methods=['GET', 'POST'])
def write():
    if 'user_id' not in session:
        flash('Vous devez être connecté pour écrire un article.')
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        category = request.form['category']
        content = request.form['content']
        file = request.files['image']

        if not title or not category or not content:
            flash('Tous les champs sont obligatoires.')
        elif len(content.split()) > 1000:
            flash('Le contenu dépasse la limite maximale de 1000 mots.')
        else:
            filepath = None
            if file and allowed_file(file.filename):
                if file.mimetype not in ['image/jpeg', 'image/png', 'image/gif']:
                    flash('Format d\'image non supporté.')
                elif len(file.read()) > 1 * 1024 * 1024:  # 1 Mo
                    flash('La taille de l\'image dépasse 1 Mo.')
                else:
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.seek(0)
                    file.save(filepath)
                    print(f"Image saved at: {filepath}")

            new_article = Article(
                title=title,
                category=category,
                content=content,
                author_id=session['user_id'],
                image_path=filepath
            )
            db.session.add(new_article)
            db.session.commit()
            flash('Article publié avec succès !')
            print("Article added successfully!")
            return redirect(url_for('home'))
    
    return render_template('write.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
