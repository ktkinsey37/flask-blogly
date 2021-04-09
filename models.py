from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

def connect_db(app):
    db.app = app
    db.init_app(app)

class User(db.Model):
    def __repr__(self):
        u = self
        return f'<User {u.id} {u.first_name} {u.last_name} {u.image_url}>'

    __tablename__ = 'users'

    id = db.Column(db.Integer,
                    primary_key=True,
                    autoincrement=True)

    first_name = db.Column(db.String(50),
                    nullable=False)

    last_name = db.Column(db.String(50))

    image_url = db.Column(db.String)

    posts = db.relationship("Post", backref="user", cascade="all, delete-orphan")

    def get_full_name(self):
        full_name = self.first_name+' '+self.last_name
        return full_name



class Post(db.Model):
    def __repr__(self):
        p = self
        return f'<Post {p.id} {p.title} {p.created_at} {p.user_id}>'

    __tablename__ = 'posts'

    id = db.Column(db.Integer,
                    primary_key=True,
                    autoincrement=True)

    title = db.Column(db.String(50),
                    nullable=False)

    content = db.Column(db.String,
                        nullable=False)

    created_at = db.Column(db.DateTime,
                        nullable=False,
                        default=datetime.utcnow)

    user_id = db.Column(
                        db.Integer,
                        db.ForeignKey('users.id'),
    )

    tags = db.relationship('Tag', secondary='posts_tags', backref="post")

class Tag(db.Model):
    __tablename__ = 'tags'

    id = db.Column(db.Integer,
                    primary_key=True,
                    autoincrement=True)

    name = db.Column(db.String(50),
                    unique=True)

    posts = db.relationship("Post", secondary='posts_tags', backref="tag", cascade="all,delete")

class PostTag(db.Model):
    __tablename__ = 'posts_tags'

    post_id = db.Column(db.Integer,
                        db.ForeignKey('posts.id'),
                        primary_key=True,
                        nullable=False)

    tag_id = db.Column(db.Integer,
                        db.ForeignKey('tags.id'),
                        primary_key=True,
                        nullable=False)                    