# app.py

from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import re
from models import db, User, Article
from config import db_config, flask_secret_key  
import logging
from logging.handlers import RotatingFileHandler
from flask import g 

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+mysqlconnector://{db_config['user']}:{db_config['password']}@{db_config['host']}/{db_config['database']}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = flask_secret_key  

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


# @app.before_request
# def log_request_info():
#     app.logger.info('Request Headers: %s', request.headers)
#     app.logger.info('Request Body: %s', request.get_data())

@app.before_request  
def load_user():  
    if 'user_id' in session:  
        g.user = User.query.get(session['user_id'])  
    else:  
        g.user = None  

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

        app.logger.info(f"Attempting to register user: {username}, {email}")

        # Vérifiez si l'adresse e-mail est valide
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash('Adresse email invalide.')
            return redirect(url_for('register'))

        # Vérifiez si l'adresse e-mail existe déjà
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Adresse e-mail déjà utilisée. Veuillez en choisir une autre.')
            return redirect(url_for('register'))

        try:
            # Hacher le mot de passe et créer un nouvel utilisateur 
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            new_user = User(username=username, email=email, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()

            flash('Inscription réussie ! Veuillez vous connecter.')
            return redirect(url_for('login'))
        except Exception as e:
            app.logger.error(f"Error during registration: {e}")
            flash('Erreur lors de l\'inscription. Veuillez réessayer.')
            return redirect(url_for('register'))

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
            session['is_admin'] = user.is_admin 
            flash('Connexion réussie !')
            return redirect(url_for('home'))
        else:
            flash('Identifiants invalides. Veuillez réessayer.')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('is_admin', None) 
    flash('Vous avez été déconnecté.')
    return redirect(url_for('home'))

@app.route('/health')
def health_check():
    return 'OK', 200

@app.route('/admin')  
def admin():  
    if 'user_id' not in session or not session.get('is_admin'):  
        flash('Accès refusé.') 
        return redirect(url_for('home'))  

    users = User.query.all()  
    articles = Article.query.all()  
    return render_template('admin.html', users=users, articles=articles)  

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


@app.route('/account', methods=['GET', 'POST'])  
def account():  
    if 'user_id' not in session:  
        flash('Vous devez être connecté pour accéder à cette page.')  
        return redirect(url_for('login'))  

    user = g.user  

    if request.method == 'POST':  
        current_password = request.form['current_password']  
        new_password = request.form['new_password']  
        confirm_password = request.form['confirm_password']  

        if not check_password_hash(user.password, current_password):  
            flash('Mot de passe actuel incorrect.')  
        elif new_password != confirm_password:  
            flash('Les nouveaux mots de passe ne correspondent pas.')  
        else:  
            user.password = generate_password_hash(new_password, method='pbkdf2:sha256')  
            db.session.commit()  
            flash('Mot de passe mis à jour avec succès.')  

    return render_template('account.html', user=user)  


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
