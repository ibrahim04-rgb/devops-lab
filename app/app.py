import os
import time
import random
from flask import Flask, jsonify, request
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)

REQUEST_COUNT = Counter(
    "app_http_requests_total",
    "Total des requêtes HTTP",
    ["method", "endpoint", "http_status"],
)

REQUEST_LATENCY = Histogram(
    "app_http_request_duration_seconds",
    "Latence des requêtes HTTP en secondes",
    ["endpoint"],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5],
)

APP_INFO = Gauge("app_info", "Informations sur l'application", ["version"])
APP_INFO.labels(version="1.0.0").set(1)


@app.before_request
def before_request():
    request.start_time = time.time()


@app.after_request
def after_request(response):
    latency = time.time() - request.start_time
    endpoint = request.path
    REQUEST_LATENCY.labels(endpoint=endpoint).observe(latency)
    REQUEST_COUNT.labels(
        method=request.method, endpoint=endpoint, http_status=response.status_code
    ).inc()
    return response


@app.route("/")
def index():
    return jsonify(
        {
            "service": "devops-lab-api",
            "version": "1.0.0",
            "status": "running",
            "endpoints": ["/", "/health", "/api/info", "/metrics"],
        }
    )


@app.route("/health")
def health():
    return jsonify({"status": "healthy"}), 200


@app.route("/api/info")
def api_info():
    r = random.random()
    if r < 0.80:
        time.sleep(random.uniform(0.001, 0.02))
    elif r < 0.95:
        time.sleep(random.uniform(0.05, 0.2))
    else:
        time.sleep(random.uniform(0.3, 0.8))
    return jsonify(
        {"hostname": os.uname().nodename, "message": "Hello from DevOps Lab API!"}
    )


@app.route("/metrics")
def metrics():
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, threaded=True)
