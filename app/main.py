import sys
import os
from ddtrace import patch_all
from flask import Flask, jsonify

patch_all()

app = Flask(__name__)
healthy = True


@app.route('/')
def home():
    return "Pipeline is working!"


@app.route('/health')
def health():
    if healthy:
        return jsonify({"status": "healthy"}), 200
    return jsonify({"status": "unhealthy"}), 500


@app.route('/kill')
def kill():
    global healthy
    healthy = False
    return jsonify({"status": "unhealthy mode activated"}), 200


@app.route('/error')
def trigger_error():
    raise Exception("Intentional error for testing!")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
