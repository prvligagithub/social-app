
import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, g


def create_app(test_config=None):
    app = Flask(__name__)

    app.config.update(
        SECRET_KEY="social-app-secret",
        DATABASE=os.path.join(app.root_path, "social.db")
    )

    if test_config:
        app.config.update(test_config)

    def get_db():
        if "db" not in g:
            g.db = sqlite3.connect(app.config["DATABASE"])
            g.db.row_factory = sqlite3.Row
            g.db.execute("PRAGMA foreign_keys = ON")
        return g.db

    @app.teardown_appcontext
    def close_db(error=None):
        db = g.pop("db", None)
        if db is not None:
            db.close()

    def init_db():
        db = get_db()

        db.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        db.execute("""
            CREATE TABLE IF NOT EXISTS likes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER NOT NULL,
                liker_name TEXT NOT NULL,
                FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
                UNIQUE (post_id, liker_name)
            )
        """)

        db.execute("""
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER NOT NULL,
                commenter_name TEXT NOT NULL,
                comment_text TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE
            )
        """)

        db.commit()

    with app.app_context():
        init_db()

    def get_posts(post_id=None):
        db = get_db()

        if post_id is None:
            rows = db.execute("""
                SELECT posts.*,
                       COUNT(DISTINCT likes.id) AS like_count
                FROM posts
                LEFT JOIN likes ON posts.id = likes.post_id
                GROUP BY posts.id
                ORDER BY posts.id DESC
            """).fetchall()
        else:
            rows = db.execute("""
                SELECT posts.*,
                       COUNT(DISTINCT likes.id) AS like_count
                FROM posts
                LEFT JOIN likes ON posts.id = likes.post_id
                WHERE posts.id = ?
                GROUP BY posts.id
            """, (post_id,)).fetchall()

        posts = []

        for row in rows:
            post = dict(row)

            post["comments"] = db.execute("""
                SELECT * FROM comments
                WHERE post_id = ?
                ORDER BY id DESC
            """, (post["id"],)).fetchall()

            posts.append(post)

        return posts

    @app.route("/")
    def index():
        posts = get_posts()
        return render_template("index.html", posts=posts)

    @app.route("/create", methods=["GET", "POST"])
    def create_post():
        if request.method == "POST":
            content = request.form.get("content", "").strip()

            if not content:
                flash("Post content cannot be empty.", "error")
                return render_template("create_post.html")

            db = get_db()
            db.execute(
                "INSERT INTO posts (content) VALUES (?)",
                (content,)
            )
            db.commit()

            flash("Post shared successfully!", "success")
            return redirect(url_for("index"))

        return render_template("create_post.html")

    @app.route("/post/<int:post_id>/like", methods=["POST"])
    def like_post(post_id):
        db = get_db()

        post = db.execute(
            "SELECT id FROM posts WHERE id = ?",
            (post_id,)
        ).fetchone()

        if post is None:
            return "Post not found", 404

        liker_name = request.form.get("liker_name", "").strip()

        if not liker_name:
            flash("Please enter your name to like the post.", "error")
            return redirect(url_for("index"))

        cursor = db.execute(
            "INSERT OR IGNORE INTO likes (post_id, liker_name) VALUES (?, ?)",
            (post_id, liker_name)
        )
        db.commit()

        if cursor.rowcount == 0:
            flash("You have already liked this post!", "error")
        else:
            flash("You liked the post!", "success")

        return redirect(url_for("index"))

    @app.route("/post/<int:post_id>/comment", methods=["POST"])
    def add_comment(post_id):
        db = get_db()

        post = db.execute(
            "SELECT id FROM posts WHERE id = ?",
            (post_id,)
        ).fetchone()

        if post is None:
            return "Post not found", 404

        commenter_name = request.form.get("commenter_name", "").strip()
        comment_text = request.form.get("comment_text", "").strip()

        if not commenter_name or not comment_text:
            flash("Please enter your name and comment.", "error")
            return redirect(url_for("index"))

        db.execute("""
            INSERT INTO comments (post_id, commenter_name, comment_text)
            VALUES (?, ?, ?)
        """, (post_id, commenter_name, comment_text))

        db.commit()

        flash("Comment added successfully!", "success")
        return redirect(url_for("index"))

    @app.route("/post/<int:post_id>")
    def post_detail(post_id):
        posts = get_posts(post_id)

        if not posts:
            return "Post not found", 404

        return render_template("index.html", posts=posts)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
