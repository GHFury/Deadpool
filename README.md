# Deadpool

A Python Flask application with a full CI/CD pipeline, Docker containerization, Datadog APM instrumentation, and a chaos engineering API for testing resilience.

## Overview

This project demonstrates a production-style DevOps workflow including automated CI/CD, containerized deployment, full observability with Datadog, and chaos engineering. On every push to main, the pipeline runs linting and unit tests, builds a Docker image tagged to the git commit hash, and is ready to deploy to Kubernetes. The chaos API allows controlled failure injection to validate self-healing and observability under stress.

## Stack

| Layer | Technology |
|---|---|
| Application | Python / Flask |
| CI/CD | GitHub Actions |
| Containerization | Docker |
| Observability | Datadog APM |
| Testing | pytest / flake8 |
| Orchestration | Kubernetes (kind) |

## Pipeline

Every push to `main` triggers the following stages in sequence:

1. Lint — flake8 enforces PEP8 code style
2. Test — pytest runs unit tests against the Flask app
3. Build — Docker image built and tagged with the git commit hash

## Getting started

```bash
git clone git@github.com:GHFury/Deadpool.git
cd Deadpool
docker build -t myapp:local .
docker run -p 8080:8080 myapp:local
```

App runs at `http://localhost:8080`

## Chaos API

The app includes a chaos engineering API for injecting controlled failures. Each endpoint targets a different failure mode that maps to a Kubernetes or Datadog observable.

| Endpoint | Method | Effect |
|---|---|---|
| `/chaos/status` | GET | Returns current chaos state |
| `/chaos/kill` | POST | Sends SIGTERM, kills the process |
| `/chaos/health` | POST | Toggles health check between 200 and 500 |
| `/chaos/latency` | POST | Injects delay into all requests |
| `/chaos/cpu` | POST | Burns CPU in a background thread |
| `/chaos/memory` | POST | Allocates a block of memory |
| `/chaos/reset` | POST | Clears all chaos conditions |

### Usage

```bash
# Check current chaos state
curl http://localhost:8080/chaos/status

# Toggle health status (liveness probe fails, pod restarts)
curl -X POST http://localhost:8080/chaos/health

# Inject 5 second delay for 30 seconds
curl -X POST -d '{"seconds":5,"duration":30}' http://localhost:8080/chaos/latency

# Burn CPU for 15 seconds
curl -X POST -d '{"seconds":15}' http://localhost:8080/chaos/cpu

# Allocate 50MB of memory
curl -X POST -d '{"mb":50}' http://localhost:8080/chaos/memory

# Kill the process (Kubernetes restarts the pod)
curl -X POST http://localhost:8080/chaos/kill

# Clear all chaos conditions
curl -X POST http://localhost:8080/chaos/reset
```

### What to observe

`/chaos/health` — Kubernetes detects the failing liveness probe and restarts the pod automatically. Watch with `kubectl get pods -w -n kube-system`.

`/chaos/kill` — The process terminates immediately. Kubernetes sees the container exit and schedules a replacement. Pod restart count increments.

`/chaos/latency` — All requests slow down including health probes. If the delay exceeds the probe timeout, Kubernetes marks the pod as unready and stops routing traffic. Datadog APM traces show the latency spike.

`/chaos/cpu` — CPU usage spikes for the specified duration. Visible in Datadog resource metrics and `kubectl top pods`.

`/chaos/memory` — Memory usage jumps by the specified amount and stays allocated until reset. Simulates a memory leak visible in Datadog and `kubectl top pods`.

## Datadog APM

The app is instrumented with `ddtrace`. To run with observability, start the Datadog agent first then pass the following environment variables at runtime:

```
DD_AGENT_HOST=dd-agent
DD_ENV=dev
DD_SERVICE=deadpool-app
DD_VERSION=1.0
```

## Project structure

```
.github/workflows/   CI/CD pipeline
app/                 Flask application
chart/               Helm chart for Kubernetes
tests/               Unit and integration tests
Dockerfile           Container build instructions
requirements.txt     Python dependencies
```

## Self-healing

The app exposes a `/health` endpoint that Kubernetes polls via a liveness probe every 5 seconds. The chaos API provides multiple ways to trigger failures and observe the recovery. Kubernetes detects the failure and automatically restarts the pod with no human intervention required.

## Development notes

Rebuild and reload after any code changes:

```bash
docker build -t deadpool-app:latest .
kind load docker-image deadpool-app:latest
kubectl rollout restart deployment deadpool -n kube-system
```
