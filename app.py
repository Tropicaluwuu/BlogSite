from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY') or 'SECRET'

db = SQLAlchemy(app)

# ==========================
# MODELS (we'll use them later)
# ==========================

class Users(db.Model):
    UserID = db.Column(db.Integer, primary_key=True)
    Username = db.Column(db.String(80), nullable=False, unique=True)
    Email = db.Column(db.String(120))
    Bio = db.Column(db.Text)

class Posts(db.Model):
    PostID = db.Column(db.Integer, primary_key=True)
    Title = db.Column(db.String(200), nullable=False)
    Content = db.Column(db.Text, nullable=False)
    CreatedAt = db.Column(db.DateTime, default=datetime.utcnow)
    UpdatedAt = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    UserID = db.Column(db.Integer, db.ForeignKey('users.UserID'), nullable=False)

class Comments(db.Model):
    CommentID = db.Column(db.Integer, primary_key=True)
    Content = db.Column(db.Text, nullable=False)
    CreatedAt = db.Column(db.DateTime, default=datetime.utcnow)
    PostID = db.Column(db.Integer, db.ForeignKey('posts.PostID'), nullable=False)
    UserID = db.Column(db.Integer, db.ForeignKey('users.UserID'), nullable=False)

class PostLikes(db.Model):
    LikeID = db.Column(db.Integer, primary_key=True)
    UserID = db.Column(db.Integer, db.ForeignKey('users.UserID'), nullable=False)
    PostID = db.Column(db.Integer, db.ForeignKey('posts.PostID'), nullable=False)





@app.route('/')
def index():
    posts = Posts.query.order_by(Posts.CreatedAt.desc()).all()
    return render_template('index.html', posts=posts)
@app.route('/posts')
def list_posts():
    posts = Posts.query.order_by(Posts.CreatedAt.desc()).all()
    return render_template('posts.html', posts=posts)

@app.route('/posts/add', methods=['GET', 'POST'])
def add_post():
    users = Users.query.all()  # choose an author
    if request.method == 'POST':
        title = request.form['title'].strip()
        content = request.form['content'].strip()
        user_id = request.form['userid']

        if not title or not content:
            flash('Title and content are required.', 'error')
            return redirect(url_for('add_post'))

        new_post = Posts(Title=title, Content=content, UserID=user_id)
        db.session.add(new_post)
        db.session.commit()
        flash('Post created successfully.', 'success')
        return redirect(url_for('list_posts'))

    return render_template('add_post.html', users=users)


@app.route('/posts/<int:id>')
def view_post(id):
    post = Posts.query.get_or_404(id)
    users = Users.query.all()
    return render_template('view_post.html', post=post, users=users)

@app.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
def edit_post(id):
    post = Posts.query.get_or_404(id)
    users = Users.query.all()

    if request.method == 'POST':
        post.Title = request.form['title'].strip()
        post.Content = request.form['content'].strip()
        post.UserID = request.form['userid']

        if not post.Title or not post.Content:
            flash('Title and content are required.', 'error')
            return redirect(url_for('edit_post', id=post.PostID))

        db.session.commit()
        flash('Post updated successfully.', 'success')
        return redirect(url_for('view_post', id=post.PostID))

    return render_template('edit_post.html', post=post, users=users)

@app.route('/posts/delete/<int:id>')
def delete_post(id):
    post = Posts.query.get_or_404(id)
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted.', 'success')
    return redirect(url_for('list_posts'))






@app.route('/users')
def list_users():
    users = Users.query.all()
    return render_template('users.html', users=users)


@app.route('/users/add', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form.get('email') or None
        bio = request.form.get('bio') or None

        if not username:
            flash('Username is required.', 'error')
            return redirect(url_for('add_user'))

        new_user = Users(Username=username, Email=email, Bio=bio)
        db.session.add(new_user)
        db.session.commit()
        flash('User created successfully.', 'success')
        return redirect(url_for('list_users'))

    return render_template('add_user.html')


@app.route('/users/edit/<int:id>', methods=['GET', 'POST'])
def edit_user(id):
    user = Users.query.get_or_404(id)

    if request.method == 'POST':
        user.Username = request.form['username'].strip()
        user.Email = request.form.get('email') or None
        user.Bio = request.form.get('bio') or None

        if not user.Username:
            flash('Username is required.', 'error')
            return redirect(url_for('edit_user', id=user.UserID))

        db.session.commit()
        flash('User updated successfully.', 'success')
        return redirect(url_for('list_users'))

    return render_template('edit_user.html', user=user)


@app.route('/users/delete/<int:id>')
def delete_user(id):
    user = Users.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted.', 'success')
    return redirect(url_for('list_users'))




@app.route('/comments/add/<int:post_id>', methods=['POST'])
def add_comment(post_id):
    post = Posts.query.get_or_404(post_id)
    content = request.form['content'].strip()
    user_id = request.form['userid']

    if not content:
        flash('Comment cannot be empty.', 'error')
        return redirect(url_for('view_post', id=post.PostID))

    comment = Comments(
        Content=content,
        PostID=post.PostID,
        UserID=user_id
    )
    db.session.add(comment)
    db.session.commit()
    flash('Comment added.', 'success')
    return redirect(url_for('view_post', id=post.PostID))


@app.route('/comments/delete/<int:id>')
def delete_comment(id):
    comment = Comments.query.get_or_404(id)
    post_id = comment.PostID
    db.session.delete(comment)
    db.session.commit()
    flash('Comment deleted.', 'success')
    return redirect(url_for('view_post', id=post_id))


@app.route('/portfolio')
def portfolio():
    return render_template('portfolio.html')


# ==========================
# LIKE ROUTE – many-to-many
# ==========================

@app.route('/posts/<int:id>/like/<int:user_id>')
def like_post(id, user_id):
    post = Posts.query.get_or_404(id)
    user = Users.query.get_or_404(user_id)

    # Avoid duplicate likes from the same user for the same post
    existing = PostLikes.query.filter_by(UserID=user.UserID, PostID=post.PostID).first()
    if not existing:
        like = PostLikes(UserID=user.UserID, PostID=post.PostID)
        db.session.add(like)
        db.session.commit()
        flash('Post liked.', 'success')
    else:
        flash('That user already liked this post.', 'error')

    return redirect(url_for('view_post', id=post.PostID))





with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
