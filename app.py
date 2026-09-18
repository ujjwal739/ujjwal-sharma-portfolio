import os
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from models import get_db, init_db, init_projects_table

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB limit

ADMIN_USERNAME = os.getenv('ADMIN_USERNAME')
ADMIN_PASSWORD_HASH = os.getenv('ADMIN_PASSWORD_HASH')
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

init_db()
init_projects_table()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == ADMIN_USERNAME and check_password_hash(ADMIN_PASSWORD_HASH, password):
            session['logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('home'))

@app.route('/admin')
@login_required
def admin_dashboard():
    db = get_db()
    certs = db.execute('SELECT * FROM certifications ORDER BY created_at DESC').fetchall()
    projs = db.execute('SELECT * FROM projects ORDER BY created_at DESC').fetchall()
    db.close()
    return render_template('admin_dashboard.html', certs=certs, projs=projs)

@app.route('/admin/certifications/add', methods=['POST'])
@login_required
def add_certification():
    title = request.form.get('title')
    issuer = request.form.get('issuer')
    date_earned = request.form.get('date_earned')
    file = request.files.get('file')

    file_name = None
    if file and file.filename and allowed_file(file.filename):
        file_name = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], file_name))

    db = get_db()
    db.execute(
        'INSERT INTO certifications (title, issuer, date_earned, file_name) VALUES (?, ?, ?, ?)',
        (title, issuer, date_earned, file_name)
    )
    db.commit()
    db.close()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/certifications/delete/<int:cert_id>', methods=['POST'])
@login_required
def delete_certification(cert_id):
    db = get_db()
    cert = db.execute('SELECT * FROM certifications WHERE id = ?', (cert_id,)).fetchone()
    if cert and cert['file_name']:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], cert['file_name'])
        if os.path.exists(file_path):
            os.remove(file_path)
    db.execute('DELETE FROM certifications WHERE id = ?', (cert_id,))
    db.commit()
    db.close()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/projects/add', methods=['POST'])
@login_required
def add_project():
    title = request.form.get('title')
    description = request.form.get('description')
    file = request.files.get('file')

    file_name = None
    if file and file.filename and allowed_file(file.filename):
        file_name = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], file_name))

    db = get_db()
    db.execute(
        'INSERT INTO projects (title, description, file_name) VALUES (?, ?, ?)',
        (title, description, file_name)
    )
    db.commit()
    db.close()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/projects/delete/<int:project_id>', methods=['POST'])
@login_required
def delete_project(project_id):
    db = get_db()
    proj = db.execute('SELECT * FROM projects WHERE id = ?', (project_id,)).fetchone()
    if proj and proj['file_name']:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], proj['file_name'])
        if os.path.exists(file_path):
            os.remove(file_path)
    db.execute('DELETE FROM projects WHERE id = ?', (project_id,))
    db.commit()
    db.close()
    return redirect(url_for('admin_dashboard'))

@app.route('/projects')
def projects():
    db = get_db()
    projs = db.execute('SELECT * FROM projects ORDER BY created_at DESC').fetchall()
    db.close()
    return render_template('projects.html', projs=projs)

@app.route('/certifications')
def certifications():
    db = get_db()
    certs = db.execute('SELECT * FROM certifications ORDER BY created_at DESC').fetchall()
    db.close()
    return render_template('certifications.html', certs=certs)

@app.route('/experience')
def experience():
    return render_template('experience.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

if __name__ == '__main__':
    app.run(debug=True)
