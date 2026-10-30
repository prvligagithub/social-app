
import sqlite3
import pytest
from app import create_app


@pytest.fixture
def app(tmp_path):
    db_path = tmp_path / "test_social.db"

    app = create_app({
        "TESTING": True,
        "SECRET_KEY": "test-secret",
        "DATABASE": str(db_path)
    })

    yield app


@pytest.fixture
def client(app):
    return app.test_client()


def create_test_post(client):
    client.post("/create", data={
        "content": "Hello everyone!"
    })


def test_homepage(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Welcome to Social App" in response.data


def test_create_post_page(client):
    response = client.get("/create")
    assert response.status_code == 200
    assert b"Create a Post" in response.data


def test_create_post_success(client, app):
    response = client.post("/create", data={
        "content": "Hello everyone! This is my first post."
    })

    assert response.status_code == 302

    with app.app_context():
        db = sqlite3.connect(app.config["DATABASE"])
        post = db.execute(
            "SELECT content FROM posts"
        ).fetchone()
        db.close()

    assert post[0] == "Hello everyone! This is my first post."


def test_empty_post(client):
    response = client.post(
        "/create",
        data={"content": ""},
        follow_redirects=True
    )

    assert b"Post content cannot be empty." in response.data


def test_whitespace_post(client):
    response = client.post(
        "/create",
        data={"content": "   "},
        follow_redirects=True
    )

    assert b"Post content cannot be empty." in response.data


def test_post_appears_on_homepage(client):
    client.post("/create", data={
        "content": "My first social media post"
    })

    response = client.get("/")
    assert b"My first social media post" in response.data


def test_like_post_success(client):
    create_test_post(client)

    response = client.post(
        "/post/1/like",
        data={"liker_name": "Siddharth"},
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"You liked the post!" in response.data
    assert b"1 Likes" in response.data


def test_duplicate_like_prevented(client):
    create_test_post(client)

    client.post(
        "/post/1/like",
        data={"liker_name": "Siddharth"}
    )

    response = client.post(
        "/post/1/like",
        data={"liker_name": "Siddharth"},
        follow_redirects=True
    )

    assert b"You have already liked this post!" in response.data
    assert b"1 Likes" in response.data


def test_different_users_can_like(client):
    create_test_post(client)

    client.post(
        "/post/1/like",
        data={"liker_name": "User1"}
    )

    client.post(
        "/post/1/like",
        data={"liker_name": "User2"}
    )

    response = client.get("/")

    assert b"2 Likes" in response.data


def test_empty_liker_name(client):
    create_test_post(client)

    response = client.post(
        "/post/1/like",
        data={"liker_name": "   "},
        follow_redirects=True
    )

    assert b"Please enter your name to like the post." in response.data
    assert b"0 Likes" in response.data


def test_like_nonexistent_post(client):
    response = client.post(
        "/post/999/like",
        data={"liker_name": "Siddharth"}
    )

    assert response.status_code == 404


def test_post_not_found(client):
    response = client.get("/post/999")
    assert response.status_code == 404