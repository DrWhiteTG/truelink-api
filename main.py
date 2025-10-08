from typing import Annotated
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import AnyHttpUrl
from truelink import TrueLinkResolver

app = FastAPI(title="TrueLink API", version="1.3.0")

# ---------- HTML pages ----------
BASE_STYLE = """
<style>
:root { color-scheme: light dark; }
* { box-sizing: border-box; }
body { font-family: system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif; margin: 0; }
.header { padding: 28px 20px; text-align: center; background: linear-gradient(135deg,#0ea5e9,#22d3ee); color: #fff; }
.header h1 { margin: 0; font-size: 28px; }
.nav { display: flex; gap: 14px; justify-content: center; padding: 12px 10px; border-bottom: 1px solid #e5e7eb22; }
.nav a { text-decoration: none; color: inherit; padding: 8px 12px; border-radius: 8px; background: #00000008; }
.container { max-width: 860px; margin: 24px auto; padding: 0 16px; }
.card { padding: 18px; border: 1px solid #e5e7eb44; border-radius: 12px; background: #ffffff0d; }
.footer { margin-top: 40px; padding: 20px; text-align: center; color: #6b7280; font-size: 14px; }
code { background: #00000012; padding: 2px 6px; border-radius: 6px; }
pre { background: #00000012; padding: 10px; border-radius: 10px; overflow: auto; }
</style>
"""

HOME_HTML = f"""
<!doctype html>
<html>
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>TrueLink API</title>
{BASE_STYLE}
</head>
<body>
  <div class="header">
    <h1>TrueLink API</h1>
    <div>Resolve direct links via query param <code>?url=</code></div>
  </div>
  <div class="nav">
    <a href="/">Home</a>
    <a href="/about">About</a>
    <a href="/tools">Tools</a>
    <a href="/docs">API Docs</a>
    <a href="/health">Health</a>
  </div>
  <div class="container">
    <div class="card">
      <h3>Quick start</h3>
      <p>Send a GET request:</p>
      <pre>https://&lt;app&gt;.herokuapp.com/?url=&lt;ENCODED_SOURCE_URL&gt;</pre>
      <p>Example with curl:</p>
      <pre>curl -s "https://&lt;app&gt;.herokuapp.com/?url=$(python3 -c 'import urllib.parse; print(urllib.parse.quote(\"https://example.com/x\", safe=\"\"))')"</pre>
    </div>
    <div class="card" style="margin-top:16px">
      <h3>Created by <a href="https://t.me/bearserver" target="_blank" rel="noopener">t.me/bearserver</a></h3>
      <p>This service is open and does not require any API key.</p>
    </div>
  </div>
  <div class="footer">
    Created by t.me/bearserver • FastAPI on Heroku
  </div>
</body>
</html>
"""

ABOUT_HTML = f"""
<!doctype html>
<html>
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>About • TrueLink API</title>
{BASE_STYLE}
</head>
<body>
  <div class="header"><h1>About</h1></div>
  <div class="nav">
    <a href="/">Home</a>
    <a href="/about">About</a>
    <a href="/tools">Tools</a>
    <a href="/docs">API Docs</a>
  </div>
  <div class="container">
    <div class="card">
      <p>This API wraps the truelink library to convert supported links into direct URLs.</p>
      <p>Use <code>/?url=&lt;ENCODED_URL&gt;</code> to resolve, or visit <a href="/docs">/docs</a> for Swagger UI.</p>
      <p>Credits: t.me/bearserver</p>
    </div>
  </div>
  <div class="footer">Created by t.me/bearserver</div>
</body>
</html>
"""

TOOLS_HTML = f"""
<!doctype html>
<html>
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Tools • TrueLink API</title>
{BASE_STYLE}
</head>
<body>
  <div class="header"><h1>Tools</h1></div>
  <div class="nav">
    <a href="/">Home</a>
    <a href="/about">About</a>
    <a href="/tools">Tools</a>
    <a href="/docs">API Docs</a>
  </div>
  <div class="container">
    <div class="card">
      <h3>URL Encoder</h3>
      <p>Encode a URL for use in the <code>?url=</code> parameter:</p>
      <pre>python3 -c 'import urllib.parse,sys; print(urllib.parse.quote(sys.argv[1], safe=""))' "https://example.com/x?a=1&amp;b=2"</pre>
      <p>JavaScript:</p>
      <pre>encodeURIComponent("https://example.com/x?a=1&b=2")</pre>
    </div>
  </div>
  <div class="footer">Created by t.me/bearserver</div>
</body>
</html>
"""

# ---------- API endpoints ----------
@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/", response_class=HTMLResponse)
async def home():
    return HOME_HTML

@app.get("/about", response_class=HTMLResponse)
async def about():
    return ABOUT_HTML

@app.get("/tools", response_class=HTMLResponse)
async def tools():
    return TOOLS_HTML

@app.get("/docs")
async def docs_redirect():
    # Redirect to FastAPI's interactive docs
    return RedirectResponse(url="/docs/")

@app.get("/resolve")
async def resolve_alias(url: Annotated[AnyHttpUrl, Query(description="Source URL to resolve")]):
    # Optional alias endpoint: /resolve?url=...
    return await resolve_get(url)

@app.get("/api/resolve")
async def resolve_api(url: Annotated[AnyHttpUrl, Query(description="Source URL to resolve")]):
    # A clean API path variant under /api
    return await resolve_get(url)

@app.get("/",
         name="resolve_get_actual")  # NOTE: not exposed; helper via direct function below
async def resolve_get(url: Annotated[AnyHttpUrl, Query(description="Source URL to resolve")]):
    url_str = str(url)
    if not TrueLinkResolver.is_supported(url_str):
        raise HTTPException(status_code=400, detail="URL not supported by truelink")
    resolver = TrueLinkResolver()
    try:
        direct = await resolver.resolve(url_str)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Resolution failed: {e}")
    return {"direct_url": str(direct)}
