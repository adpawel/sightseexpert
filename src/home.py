import os
import time
from flask import Blueprint, flash, g, redirect, render_template, request, url_for, send_from_directory
from werkzeug.exceptions import abort
from src.auth import login_required
from src.db import get_db

bp = Blueprint('home', __name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

@bp.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@bp.route('/place/filter')
def filter():
    author = request.args.get('username')
    street = request.args.get('street')
    db = get_db()

    query = '''
        SELECT p.id, title, body, created, author_id, username, picture, address
        FROM place p JOIN "user" u ON p.author_id = u.id
    '''

    conditions = []
    params = []

    if author:
        conditions.append("username = %s")
        params.append(author)
    if street:
        conditions.append("address LIKE %s")
        params.append(f"%{street}%")

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY created DESC"

    # Using cursor to execute the query
    with db.cursor() as cursor:
        cursor.execute(query, params)
        places = cursor.fetchall()

    return render_template('home/index.html', places=places)

@bp.route('/place/author')
def get_by_author():
    author = request.args.get('username', '')
    db = get_db()

    with db.cursor() as cursor:
        cursor.execute(
            '''
            SELECT p.id, title, body, created, author_id, username, picture, address
            FROM place p JOIN "user" u ON p.author_id = u.id
            WHERE username = %s
            ORDER BY created DESC
            ''', (author,)
        )
        places = cursor.fetchall()

    return render_template('home/index.html', places=places)

@bp.route('/place/street')
def get_by_street():
    street = request.args.get('street', '')  
    db = get_db()

    with db.cursor() as cursor:
        cursor.execute(
            '''
            SELECT p.id, title, body, created, author_id, username, picture, address
            FROM place p JOIN "user" u ON p.author_id = u.id
            WHERE address LIKE %s
            ORDER BY created DESC
            ''', ("%"+street+"%",)  
        )
        places = cursor.fetchall()

    return render_template('home/index.html', places=places)

@bp.route('/')
def index():
    db = get_db()

    # Create a cursor from the db connection
    with db.cursor() as cursor:
        cursor.execute(
            '''
            SELECT p.id, title, body, created, author_id, username, picture, address
            FROM place p JOIN "user" u ON p.author_id = u.id
            ORDER BY created DESC
            '''
        )
        places = cursor.fetchall()  # Fetch all rows from the executed query

    return render_template('home/index.html', places=places)

def allowed_file(filename):
    """ Check if the file has an allowed extension """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_filename(filename):
    ext = os.path.splitext(filename)[1]
    timestamp = int(time.time())
    return f"{timestamp}{ext}"

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        address = request.form['address']
        file = request.files['file']
        error = None
        picture_path = None

        if not title:
            error = 'Title is required.'
        elif not address:
            error = 'Address is required'

        if file and allowed_file(file.filename):
            filename = generate_filename(file.filename)
            picture_path = os.path.join('src', UPLOAD_FOLDER, filename)
            file.save(picture_path)

        if error is not None:
            flash(error)
        else:
            db = get_db()
            with db.cursor() as cursor:
                cursor.execute(
                    '''
                    INSERT INTO place (title, body, author_id, address, picture)
                    VALUES (%s, %s, %s, %s, %s)
                    ''',
                    (title, body, g.user['id'], address, filename)
                )
                db.commit()
            return redirect(url_for('home.index'))

    return render_template('home/create.html')

def get_place(id, check_author=True):
    db = get_db()

    with db.cursor() as cursor:
        cursor.execute(
            '''
            SELECT p.id, title, body, created, author_id, username, address, picture
            FROM place p JOIN "user" u ON p.author_id = u.id
            WHERE p.id = %s
            ''', (id,)
        )
        place = cursor.fetchone()

    if place is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and place['author_id'] != g.user['id']:
        abort(403)

    return place

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    place = get_place(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        address = request.form['address']
        file = request.files['file'] #or place['picture']
        error = None
        picture_path = None

        if not title:
            error = 'Title is required.'

        if not address:
            error = 'Address is required.'
            
        # poprawic    
        if not file:
            error = 'File is required'

        if file and allowed_file(file.filename):
            filename = generate_filename(file.filename)
            remove_picture(os.path.join('src', UPLOAD_FOLDER, place['picture']))
            picture_path = os.path.join('src', UPLOAD_FOLDER, filename)
            file.save(picture_path)

        if error is not None:
            flash(error)
        else:
            db = get_db()
            with db.cursor() as cursor:
                cursor.execute(
                    '''
                    UPDATE place SET title = %s, body = %s, address = %s, picture = %s
                    WHERE id = %s
                    ''',
                    (title, body, address, filename, id)
                )
                db.commit()
            return redirect(url_for('home.index'))

    return render_template('home/update.html', place=place)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    place = get_place(id)
    db = get_db()

    if place and place['picture']:
        remove_picture(place['picture'])

    with db.cursor() as cursor:
        cursor.execute('DELETE FROM place WHERE id = %s', (id,))
        db.commit()

    return redirect(url_for('home.index'))

def remove_picture(picture_path):
    if os.path.exists(picture_path):
        os.remove(picture_path)
