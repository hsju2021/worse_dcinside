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
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    username = db.Column(db.String(20), nullable=False, default='Anonymous')

# Form for creating/editing posts
class PostForm(FlaskForm):
    title = StringField('Title')
    content = TextAreaField('Content')
    submit = SubmitField('Post')
    username = StringField('Username', validators=[DataRequired()])

migrate = Migrate(app, db)

@app.route('/')
def index():
    posts = Post.query.all()  # Fetch all posts from the database
    return render_template('index.html', posts=posts)

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

if __name__ == '__main__':
    app.run(debug=True)
