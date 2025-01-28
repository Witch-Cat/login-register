import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Crée le dossier 'instance' s'il n'existe pas
instance_folder = os.path.join(os.getcwd(), 'instance')
if not os.path.exists(instance_folder):
    os.makedirs(instance_folder)

# Configuration de la base de données
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Définir une clé secrète
app.config['SECRET_KEY'] = 'rpajeapjeaspzjeapmnsp'  # Clé secrète fixe

db = SQLAlchemy(app)

# Modèle de base de données
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(30), nullable=False)
    account_type = db.Column(db.String(50), nullable=False)  # professeur, professeur principal, élève

# Fonction pour créer la base de données
def create_database():
    with app.app_context():
        db.create_all()
        print("Base de données créée avec succès.")
        
        # Crée un utilisateur de test si la table est vide
        if not User.query.first():  # Vérifie si la base est vide
            test_user = User(
                first_name='John',
                last_name='Doe',
                email='john.doe@example.com',
                password='password123',  # Assure-toi de hacher le mot de passe en production
                account_type='élève'
            )
            db.session.add(test_user)
            db.session.commit()
        
        print("Utilisateur de test ajouté.")

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']
        account_type = request.form['account_type']

        # Vérifie si l'email existe déjà
        if User.query.filter_by(email=email).first():
            flash('Cet email est déjà utilisé.', 'danger')
            return redirect(url_for('register'))

        new_user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
            account_type=account_type
        )
        db.session.add(new_user)
        db.session.commit()

        flash('Inscription réussie !', 'success')
        return redirect(url_for('index'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email, password=password).first()

        if user:
            # L'utilisateur est trouvé, on le connecte en stockant son ID dans la session
            session['user_id'] = user.id
            flash(f'Bienvenue, {user.first_name}!', 'success')

            # Rendre directement le template correspondant au type d'utilisateur
            if user.account_type == 'élève':
                return render_template('student_space.html', user=user)
            elif user.account_type == 'professeur':
                return render_template('teacher_space.html', user=user)
            elif user.account_type == 'professeur_principal':
                return render_template('head_teacher_space.html', user=user)
        else:
            flash('Email ou mot de passe incorrect.', 'danger')
    return render_template('login.html')


@app.route('/student_space')
def student_space():
    user = User.query.get(session.get('user_id'))
    return render_template('student_space.html', user=user)

@app.route('/teacher_space')
def teacher_space():
    user = User.query.get(session.get('user_id'))
    return render_template('teacher_space.html', user=user)

@app.route('/head_teacher_space')
def head_teacher_space():
    user = User.query.get(session.get('user_id'))
    return render_template('head_teacher_space.html', user=user)

if __name__ == '__main__':
    # Ajout d'une commande pour créer la base de données
    import sys
    if 'create_db' in sys.argv:
        create_database()
    else:
        # Crée la base de données au démarrage si nécessaire
        with app.app_context():
            db.create_all()
        app.run(debug=True)
