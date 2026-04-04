from ddtrace import patch_all
from flask import Flask

patch_all()

app = Flask(__name__)


@app.route('/')
def home():
    return "Pipeline is working!"


@app.route('/error')
def trigger_error():
    raise Exception("Intentional error for testing!")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
