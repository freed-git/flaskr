import functools
from flask import current_app
import sqlite3
from contextlib import closing

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            # try:
            #     db.execute(
            #         "INSERT INTO user (username, password) VALUES (?, ?)",
            #         (username, generate_password_hash(password)),
            #     )
            #     db.commit()
            # except db.IntegrityError:
            #     error = f"User {username} is already registered."
            # else:
            #     return redirect(url_for("auth.login"))

            database = current_app.config['DATABASE']
            detect_types = sqlite3.PARSE_DECLTYPES

            with closing(sqlite3.connect(database=database, detect_types=detect_types)) as connection:
                try:
                    connection.row_factory = sqlite3.Row
                    with closing(connection.cursor()) as cursor:
                        cursor.execute(
                            "INSERT INTO user (username, password) VALUES (?, ?)",
                            (username, generate_password_hash(password)),
                        )
                    connection.commit()
                except connection.IntegrityError:
                    error = f"User {username} is already registered."
                else:
                    return redirect(url_for("auth.login"))

        flash(error)

    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # db = get_db()
        error = None
        # user = db.execute(
        #     'SELECT * FROM user WHERE username = ?', (username,)
        # ).fetchone()

        database = current_app.config['DATABASE']
        detect_types = sqlite3.PARSE_DECLTYPES

        with closing(sqlite3.connect(database=database, detect_types=detect_types)) as connection:
            connection.row_factory = sqlite3.Row
            with closing(connection.cursor()) as cursor:
                user = cursor.execute(
                    'SELECT * FROM user WHERE username = ?', (username,)
                ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        # g.user = get_db().execute(
        #     'SELECT * FROM user WHERE id = ?', (user_id,)
        # ).fetchone()
        database = current_app.config['DATABASE']
        detect_types = sqlite3.PARSE_DECLTYPES

        with closing(sqlite3.connect(database=database, detect_types=detect_types)) as connection:
            connection.row_factory = sqlite3.Row
            with closing(connection.cursor()) as cursor:
                g.user = cursor.execute(
                    'SELECT * FROM user WHERE id = ?', (user_id,)
                ).fetchone()

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
