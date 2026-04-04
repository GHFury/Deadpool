import sys
import os

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../..')
))

from app.main import app  # noqa: E402


def test_home():
    client = app.test_client()
    response = client.get('/')
    assert response.status_code == 200
    assert b"Pipeline is working!" in response.data
