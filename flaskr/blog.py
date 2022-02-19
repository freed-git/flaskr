from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db, close_db
from flask import current_app
import sqlite3
from contextlib import closing
from functools import wraps
from opentelemetry import trace
from prometheus_client import Counter

bp = Blueprint('blog', __name__)

tracer = trace.get_tracer_provider().get_tracer(__name__)
from prometheus_client import REGISTRY

blog_counter = Counter('blog', 'blog count', ['method', 'endpoint'], registry=REGISTRY)

def add_trace(f):

    @wraps(f)
    def wrapper(*args, **kwargs):
        with tracer.start_as_current_span(f.__name__):
            result = f(*args, **kwargs)

        return result

    return wrapper


@bp.route('/')
def index():
    current_app.logger.info("blog index")
    blog_counter.labels(request.method, request.path).inc(exemplar={'traceID': str(trace.get_current_span().context.trace_id)})

    # db = get_db()
    # posts = db.execute(
    #     'SELECT p.id, title, body, created, author_id, username'
    #     ' FROM post p JOIN user u ON p.author_id = u.id'
    #     ' ORDER BY created DESC'
    # ).fetchall()

    database = current_app.config['DATABASE']
    detect_types = sqlite3.PARSE_DECLTYPES

    with closing(sqlite3.connect(database=database, detect_types=detect_types)) as connection:
        connection.row_factory = sqlite3.Row
        with closing(connection.cursor()) as cursor:
            posts = cursor.execute(
                'SELECT p.id, title, body, created, author_id, username'
                ' FROM post p JOIN user u ON p.author_id = u.id'
                ' ORDER BY created DESC'
            ).fetchall()

    return render_template('blog/index.html', posts=posts)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    current_app.logger.info("blog create")
    blog_counter.labels(request.method, request.path).inc(exemplar={'traceID': str(trace.get_current_span().context.trace_id)})

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            # db = get_db()
            # db.execute(
            #     'INSERT INTO post (title, body, author_id)'
            #     ' VALUES (?, ?, ?)',
            #     (title, body, g.user['id'])
            # )
            # db.commit()

            database = current_app.config['DATABASE']
            detect_types = sqlite3.PARSE_DECLTYPES

            with closing(sqlite3.connect(database=database, detect_types=detect_types)) as connection:
                connection.row_factory = sqlite3.Row
                with closing(connection.cursor()) as cursor:
                    posts = cursor.execute(
                        'INSERT INTO post (title, body, author_id)'
                        ' VALUES (?, ?, ?)',
                        (title, body, g.user['id'])
                    )
                connection.commit()

            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')

@add_trace
def get_post(id, check_author=True):
    current_app.logger.info("blog get_post")

    # post = get_db().execute(
    #     'SELECT p.id, title, body, created, author_id, username'
    #     ' FROM post p JOIN user u ON p.author_id = u.id'
    #     ' WHERE p.id = ?',
    #     (id,)
    # ).fetchone()

    database = current_app.config['DATABASE']
    detect_types = sqlite3.PARSE_DECLTYPES

    with closing(sqlite3.connect(database=database, detect_types=detect_types)) as connection:
        connection.row_factory = sqlite3.Row
        with closing(connection.cursor()) as cursor:
            post = cursor.execute(
                'SELECT p.id, title, body, created, author_id, username'
                ' FROM post p JOIN user u ON p.author_id = u.id'
                ' ORDER BY created DESC'
            ).fetchone()

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    current_app.logger.info("blog update")
    blog_counter.labels(request.method, request.path).inc(exemplar={'traceID': str(trace.get_current_span().context.trace_id)})

    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            # db = get_db()
            # db.execute(
            #     'UPDATE post SET title = ?, body = ?'
            #     ' WHERE id = ?',
            #     (title, body, id)
            # )
            # db.commit()

            database = current_app.config['DATABASE']
            detect_types = sqlite3.PARSE_DECLTYPES

            with closing(sqlite3.connect(database=database, detect_types=detect_types)) as connection:
                connection.row_factory = sqlite3.Row
                with closing(connection.cursor()) as cursor:
                    posts = cursor.execute(
                        'UPDATE post SET title = ?, body = ?'
                        ' WHERE id = ?',
                        (title, body, id)
                    )
                connection.commit()


            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    current_app.logger.info("blog delete")
    blog_counter.labels(request.method, request.path).inc(exemplar={'traceID': str(trace.get_current_span().context.trace_id)})

    get_post(id)
    # db = get_db()
    # db.execute('DELETE FROM post WHERE id = ?', (id,))
    # db.commit()

    database = current_app.config['DATABASE']
    detect_types = sqlite3.PARSE_DECLTYPES

    with closing(sqlite3.connect(database=database, detect_types=detect_types)) as connection:
        connection.row_factory = sqlite3.Row
        with closing(connection.cursor()) as cursor:
            posts = cursor.execute(
                'DELETE FROM post WHERE id = ?', (id,)
            )
        connection.commit()

    return redirect(url_for('blog.index'))
