import sys
import os
from app.main import app

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../..')
))


def test_home():
    client = app.test_client()
    response = client.get('/')
    assert response.status_code == 200
    assert b"Pipeline is working!" in response.data
