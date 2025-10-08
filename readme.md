# TrueLink API

Resolve supported links into direct URLs using a lightweight FastAPI wrapper around the truelink Python library. [web:12]

[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://www.heroku.com/deploy?template=https://github.com/DrWhiteTG/truelink-api) [web:84]

## Features
- Query-style resolution: `/?url=<ENCODED_URL>` returns `{"direct_url": "..."}` if supported. [web:12]
- No API key required; simple GET usage from browser or curl. [web:12]
- Auto-generated Swagger UI at `/docs` and a health endpoint at `/health`. [web:12]

## Quick start

### Run locally
- Install dependencies: `pip install -r requirements.txt` [web:12]
- Start dev server: `uvicorn main:app --reload` and open `http://127.0.0.1:8000/` [web:12]

### Example resolve
- Browser: `http://127.0.0.1:8000/?url=<ENCODED_URL>` [web:12]
- Curl:
  - `curl -s "http://127.0.0.1:8000/?url=$(python3 -c 'import urllib.parse;print(urllib.parse.quote(\"https://example.com/x?a=1&b=2\", safe=\"\"))')"` [web:12]

## Deploy to Heroku

### One‑click button
- Click the button at the top of this README to deploy via app.json directly from GitHub. [web:84]

### CLI alternative
- `heroku login` [web:12]
- `heroku create truelink-api-demo` [web:12]
- `git push heroku main` [web:12]
- `heroku ps:scale web=1` [web:12]
- `heroku open` [web:12]

## Endpoints

- `GET /` — Home page with quick usage and credit line “Created by t.me/bearserver.” [web:12]
- `GET /health` — Liveness check returns `{"status":"ok"}`. [web:12]
- `GET /docs` — Interactive Swagger UI. [web:12]
- `GET /?url=<ENCODED_URL>` — Resolve to direct link JSON. [web:12]
- `GET /resolve?url=<ENCODED_URL>` — Alias for resolve. [web:12]
- `GET /api/resolve?url=<ENCODED_URL>` — API‑namespaced path. [web:12]

## URL encoding tips

- Always URL‑encode the full value passed to the `url` query parameter, especially when it contains `?` or `&`. [web:84]
- JavaScript: `encodeURIComponent("https://example.com/x?a=1&b=2")` [web:84]
- Python: `urllib.parse.quote("https://example.com/x?a=1&b=2", safe="")` [web:84]

## Requirements

- `requirements.txt`, `Procfile`, and `runtime.txt` should be present so Heroku detects Python and boots Gunicorn correctly. [web:12]
- The Heroku deploy button reads `app.json` in the repo root to preconfigure buildpacks/env on deploy. [web:84]

## Credit

- Created by t.me/bearserver. [web:84]
