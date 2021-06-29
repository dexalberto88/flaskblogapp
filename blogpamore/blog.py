from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from .models import User, Post
from .auth import login_required
from . import db

bp = Blueprint('blog', __name__)

@bp.route('/')
@login_required
def index():
    posts = Post.query.all()
    return render_template('blog/index.html', posts=posts)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form.get('title')
        body = request.form.get('body')
        error = None

        if not title:
            error = 'Title is required.'
        
        if error is not None:
            flash(error)
        else:
            new_post = Post(title=title, body=body, author=g.user.first_name, user_id=g.user.id)
            db.session.add(new_post)
            db.session.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')

def get_post(id, check_author=True):
    post = Post.query.filter_by(id=id).first()
    
    if post is None:
        abort(404, f'Post id {id} doesn\'t exist.')
    
    if check_author and post.user_id != g.user.id:
        abort(403, f'Forbidden')

    return post

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
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
            post.title = title
            post.body = body
            db.session.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)

@bp.route('/<int:id>/delete', methods=('POST','GET'))
@login_required
def delete(id):
    post = get_post(id)

    if post.user_id == g.user.id:
        db.session.delete(post)
        db.session.commit()
    return redirect(url_for('blog.index'))
