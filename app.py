
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

        db.commit()

    with app.app_context():
        init_db()

    @app.route("/")
    def index():
        posts = get_db().execute(
            "SELECT * FROM posts ORDER BY id DESC"
        ).fetchall()

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

    @app.route("/post/<int:post_id>")
    def post_detail(post_id):

        post = get_db().execute(
            "SELECT * FROM posts WHERE id = ?",
            (post_id,)
        ).fetchone()

        if post is None:
            return "Post not found", 404

        return render_template("index.html", posts=[post])

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
