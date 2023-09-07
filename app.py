from datetime import datetime
from flask import Flask, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from flask_migrate import Migrate
from wtforms.validators import DataRequired

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = 'your_secret_key'  # This should be a random string for security purposes
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

# Initialize database
db = SQLAlchemy(app)

# Database model for posts
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=True)
    content = db.Column(db.Text, nullable=True)
    username = db.Column(db.String(20), nullable=True, default='Anonymous')
    comments = db.relationship('Comment', backref='post', lazy=True, cascade="all, delete-orphan")
    date_posted = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)

# Form for creating/editing posts
class PostForm(FlaskForm):
    title = StringField('Title')
    content = TextAreaField('Content')
    submit = SubmitField('Post')
    username = StringField('Username', validators=[DataRequired()])

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=True)
    username = db.Column(db.String(100), nullable=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=True)

class CommentForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    content = TextAreaField('Comment', validators=[DataRequired()])
    submit = SubmitField('Post Comment')

migrate = Migrate(app, db)

@app.route('/')
def index():
    posts = Post.query.order_by(Post.date_posted.desc()).all()  # Fetch all posts from the database
    comment_form = CommentForm()
    return render_template('index.html', posts=posts, comment_form=comment_form)

@app.route('/posts', methods=['GET', 'POST'])
def posts():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, username=form.username.data)
        db.session.add(post)
        db.session.commit()
        flash('Post created successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('post.html', form=form)

@app.route('/delete_post/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash('Post has been deleted!', 'success')
    return redirect(url_for('index'))

@app.route('/add_comment/<int:post_id>', methods=['POST'])
def add_comment(post_id):
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(content=form.content.data, username=form.username.data, post_id=post_id)
        db.session.add(comment)
        db.session.commit()
        flash('Comment added!', 'success')
    return redirect(url_for('index'))

@app.route('/delete_comment/<int:comment_id>', methods=['POST'])
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    db.session.delete(comment)
    db.session.commit()
    flash('Comment has been deleted!', 'success')
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
