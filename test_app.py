
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

    assert response.status_code == 200
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


def test_multiple_posts(client):
    client.post("/create", data={"content": "First post"})
    client.post("/create", data={"content": "Second post"})

    response = client.get("/")

    assert b"First post" in response.data
    assert b"Second post" in response.data


def test_post_not_found(client):
    response = client.get("/post/999")
    assert response.status_code == 404
