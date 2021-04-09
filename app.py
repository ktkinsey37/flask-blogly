"""Blogly application."""

from flask import Flask, request, render_template, redirect, flash, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Post, Tag, PostTag

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

connect_db(app)
db.create_all()


@app.route('/', methods=["GET"])
def homepage():
    return redirect("/users", code=302)

@app.route('/users', methods=["GET"])
def users_list():
    users = User.query.all()
    title = 'Users'
    return render_template('users.html', title=title, users=users)

@app.route('/users/new', methods=["GET"])
def add_user_form():
    title = 'Add A New User'
    return render_template('users_new.html', title=title)

@app.route('/users/new', methods=["POST"])
def add_user_post():
    first_name, last_name, image = request.form.get("fname"), request.form.get("lname"), request.form.get("image")
    new_user = User(first_name=f'{first_name}', last_name=f'{last_name}', image_url=f'{image}')
    db.session.add(new_user)
    db.session.commit()
    return redirect("/users", code=302)

@app.route('/users/<user_id>', methods=["GET"])
def user(user_id):
    user_id = int(user_id)
    user = User.query.get_or_404(user_id)
    posts = Post.query.filter_by(user_id=f'{user_id}').all()
    return render_template('user_view.html', user=user, posts=posts)
    
@app.route('/users/<user_id>/edit', methods=["GET"])
def user_edit(user_id):
    user_id = int(user_id)
    user = User.query.get_or_404(user_id)
    return render_template('user_edit.html', user=user)

@app.route('/users/<user_id>/edit', methods=["POST"])
def user_edit_post(user_id):
    user_id = int(user_id)
    first_name, last_name, image = request.form.get("fname"), request.form.get("lname"), request.form.get("image")
    user = User.query.get_or_404(user_id)
    user.first_name = first_name
    user.last_name = last_name
    user.image_url = image
    db.session.add(user)
    db.session.commit()
    return render_template('user_view.html', user=user)


@app.route('/users/<user_id>/delete', methods=["POST"])
def user_id_page(user_id):
    user_id = int(user_id)
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    users = User.query.all()
    title = 'Users'
    return render_template('users.html', title=title, users=users)

@app.route('/users/<user_id>/posts/new', methods=["GET"])
def user_edit_blog(user_id):
    # JUST NEED TO SHOW THE ADD A BLOG POST FORM
    user_id = int(user_id)
    user = User.query.get_or_404(user_id)
    tags = Tag.query.all()
    return render_template('post_new.html', user=user, tags=tags)

@app.route('/users/<user_id>/posts/new', methods=["POST"])
def user_edit_blog_post(user_id):
    user_id = int(user_id)
    title, content = request.form.get("title"), request.form.get("content")
    new_post = Post(title=f'{title}', content=f'{content}', user_id=f'{user_id}')
    tag_ids = request.form.getlist('tag')
    new_post.tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()
    db.session.add(new_post)
    db.session.commit()
    return redirect(f'/posts/{new_post.id}', code=302)

@app.route('/posts/<post_id>', methods=["GET"])
def blog_post_view(post_id):
    post = Post.query.get_or_404(int(post_id))
    user = User.query.filter_by(id=f'{post.user_id}').one()
    tags = post.tags
    return render_template('post_view.html', post=post, user=user, tags=tags)

@app.route('/posts/<post_id>/edit', methods=["GET"])
def blog_post_edit(post_id):
    post_id = int(post_id)
    post = Post.query.get_or_404(post_id)
    tags = Tag.query.all()
    return render_template('post_edit.html', post=post, tags=tags)

@app.route('/posts/<post_id>/edit', methods=["POST"])
def blog_post_edit_post(post_id):
    post = Post.query.get_or_404(int(post_id))
    post.title, post.content = request.form.get("title"), request.form.get("content")
    tag_ids = request.form.getlist('tag')
    post.tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()
    for tag in Tag.query.filter(Tag.id.in_(tag_ids)).all():
        tag.posts.append(post)
        db.session.add(tag)
    db.session.add(post)
    db.session.commit()
    user = User.query.filter_by(id=f'{post.user_id}').one()
    return render_template('post_view.html', post=post, user=user, tags=post.tags)

@app.route('/posts/<post_id>/delete', methods=["POST"])
def blog_post_delete_post(post_id):
    post_id = int(post_id)
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    user = User.query.filter_by(id=f'{post.user_id}').one()
    posts = Post.query.filter_by(user_id=f'{user.id}').all()
    return render_template('user_view.html', user=user, posts=posts)

@app.route('/tags', methods=["GET"])
def view_all_tags():
    tags = Tag.query.all()
    return render_template('tags_all.html', tags=tags, title="All Tags")

@app.route('/tags/<tag_id>', methods=["GET"])
def view_tag_by_id(tag_id):
    tag_id = int(tag_id)
    tag = Tag.query.get_or_404(tag_id)
    return render_template('tag_show.html', tag=tag)

@app.route('/tags/new', methods=["GET"])
def view_new_tag_form():
    return render_template('tag_new.html')

@app.route('/tags/new', methods=["POST"])
def create_new_tag():
    tag = request.form.get("tag")
    new_tag = Tag(name=f'{tag}')
    db.session.add(new_tag)
    db.session.commit()
    return redirect('/tags', code=302)

@app.route('/tags/<tag_id>/edit', methods=["GET"])
def edit_tag_form(tag_id):
    tag_id = int(tag_id)
    tag = Tag.query.get_or_404(tag_id)
    posts = Post.query.all()
    return render_template('tag_edit.html', tag=tag, posts=posts)
   
@app.route('/tags/<tag_id>/edit', methods=["POST"])
def edit_tag(tag_id):
    tag_id = int(tag_id)
    name = request.form.get("tag")
    tag = Tag.query.get_or_404(tag_id)
    tag.name = name
    db.session.add(tag)
    db.session.commit()
    tags = Tag.query.all()
    return redirect('/tags', code=302)

@app.route('/tags/<tag_id>/delete', methods=["POST"])
def delete_tag_by_id(tag_id):
    tag_id = int(tag_id)
    tag = Tag.query.get_or_404(tag_id)
    db.session.delete(tag)
    db.session.commit()
    return redirect('/tags', code=302)


# # posts = Post.query.filter_by(user_id=f'{user_id}', post_id=f'{post_id}').all()

# # ORRRR

# # posts = Post.query.filter(Post.user_id > 3,id == 2).all()
