from ddtrace import patch_all
from flask import Flask, jsonify, request
import threading
import time
import os
import signal

patch_all()

app = Flask(__name__)

# Chaos state
chaos_state = {
    "healthy": True,
    "latency_seconds": 0,
    "latency_until": 0,
    "memory_blob": None,
    "cpu_active": False,
}


@app.before_request
def inject_latency():
    if (
        chaos_state["latency_seconds"] > 0
        and time.time() < chaos_state["latency_until"]
    ):
        time.sleep(chaos_state["latency_seconds"])
    elif chaos_state["latency_seconds"] > 0:
        chaos_state["latency_seconds"] = 0


@app.route('/')
def home():
    return "Pipeline is working!"


@app.route('/health')
def health():
    if chaos_state["healthy"]:
        return jsonify({"status": "healthy"}), 200
    return jsonify({"status": "unhealthy"}), 500


# --- Chaos Endpoints ---

@app.route('/chaos/status')
def chaos_status():
    latency_active = (
        time.time() < chaos_state["latency_until"]
    )
    memory_blob = chaos_state["memory_blob"]
    return jsonify({
        "healthy": chaos_state["healthy"],
        "latency_seconds": (
            chaos_state["latency_seconds"]
            if latency_active else 0
        ),
        "memory_allocated_mb": (
            len(memory_blob) / (1024 * 1024)
            if memory_blob else 0
        ),
        "cpu_burn_active": chaos_state["cpu_active"],
    }), 200


@app.route('/chaos/kill', methods=['POST'])
def chaos_kill():
    """Crashes the process.

    Kubernetes liveness probe fails, pod restarts.
    """
    os.kill(os.getpid(), signal.SIGTERM)
    return jsonify({"status": "killing process"}), 200


@app.route('/chaos/health', methods=['POST'])
def chaos_health():
    """Toggles health status.

    Liveness probe returns 500, triggers pod restart.
    """
    chaos_state["healthy"] = not chaos_state["healthy"]
    status = (
        "healthy" if chaos_state["healthy"]
        else "unhealthy"
    )
    return jsonify({"status": status}), 200


@app.route('/chaos/latency', methods=['POST'])
def chaos_latency():
    """Adds artificial delay to all requests.

    Body: {"seconds": 5, "duration": 30}
    """
    data = request.get_json(
        force=True, silent=True
    ) or {}
    delay = data.get("seconds", 3)
    duration = data.get("duration", 30)
    chaos_state["latency_seconds"] = delay
    chaos_state["latency_until"] = (
        time.time() + duration
    )
    return jsonify({
        "status": "latency injected",
        "delay_seconds": delay,
        "duration_seconds": duration,
    }), 200


@app.route('/chaos/cpu', methods=['POST'])
def chaos_cpu():
    """Burns CPU for N seconds.

    Visible in Datadog resource metrics.
    Body: {"seconds": 10}
    """
    data = request.get_json(
        force=True, silent=True
    ) or {}
    burn_time = data.get("seconds", 10)

    def burn():
        chaos_state["cpu_active"] = True
        end = time.time() + burn_time
        while time.time() < end:
            _ = sum(
                i * i for i in range(10000)
            )
        chaos_state["cpu_active"] = False

    thread = threading.Thread(
        target=burn, daemon=True
    )
    thread.start()
    return jsonify({
        "status": "cpu burn started",
        "seconds": burn_time,
    }), 200


@app.route('/chaos/memory', methods=['POST'])
def chaos_memory():
    """Allocates memory to simulate a leak.

    Body: {"mb": 50}
    """
    data = request.get_json(
        force=True, silent=True
    ) or {}
    mb = data.get("mb", 50)
    chaos_state["memory_blob"] = bytearray(
        mb * 1024 * 1024
    )
    return jsonify({
        "status": "memory allocated",
        "mb": mb,
    }), 200


@app.route('/chaos/reset', methods=['POST'])
def chaos_reset():
    """Clears all chaos and returns to normal."""
    chaos_state["healthy"] = True
    chaos_state["latency_seconds"] = 0
    chaos_state["latency_until"] = 0
    chaos_state["memory_blob"] = None
    chaos_state["cpu_active"] = False
    return jsonify({"status": "all chaos cleared"}), 200


@app.route('/error')
def trigger_error():
    raise Exception("Intentional error for testing!")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
