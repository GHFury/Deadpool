# Deadpool

A Python Flask application with a full CI/CD pipeline, Docker containerization, and Datadog APM instrumentation.

## Overview

This project demonstrates a production-style DevOps workflow including automated CI/CD, containerized deployment, and full observability with Datadog. On every push to main, the pipeline runs linting and unit tests, builds a Docker image tagged to the git commit hash, and is ready to deploy to Kubernetes.

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

The app exposes a `/health` endpoint that Kubernetes polls via
a liveness probe every 5 seconds. Hitting `/kill` simulates a
failure by returning 500 on health checks. Kubernetes detects
the failure and automatically restarts the pod — no human
intervention required.
