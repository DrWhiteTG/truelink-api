import os
from typing import Optional, Annotated

from fastapi import FastAPI, HTTPException, Depends, Query, Header
from pydantic import AnyHttpUrl
from truelink import TrueLinkResolver

# Configure API key (env var overrides default)
APP_KEY = os.getenv("APP_KEY", "bearserver")

app = FastAPI(title="TrueLink API", version="1.2.0")

def key_from_query_or_header(
    key: Optional[str] = Query(default=None, description="API key in query string"),
    x_key: Optional[str] = Header(default=None, alias="x-key", description="API key in header"),
) -> str:
    """
    Accept API key either as query param ?key=... or header x-key: ...
    Raises:
      401 if missing
      403 if invalid
    """
    token = key or x_key
    if token is None:
        raise HTTPException(status_code=401, detail="Missing API key")
    if token != APP_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return token

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/", dependencies=[Depends(key_from_query_or_header)])
async def resolve_get(
    url: Annotated[AnyHttpUrl, Query(description="Source URL to resolve, e.g., https://example.com/xyz")],
):
    """
    Resolve a supported URL to its direct link via query params:
      GET /?url=<encoded_url>&key=bearserver
    """
    url_str = str(url)
    if not TrueLinkResolver.is_supported(url_str):
        raise HTTPException(status_code=400, detail="URL not supported by truelink")
    resolver = TrueLinkResolver()
    try:
        direct = await resolver.resolve(url_str)
    except Exception as e:
        # Upstream or processing failure
        raise HTTPException(status_code=502, detail=f"Resolution failed: {e}")
    return {"direct_url": str(direct)}

@app.post("/", dependencies=[Depends(key_from_query_or_header)])
async def resolve_post(
    url: Annotated[AnyHttpUrl, Query(description="Source URL to resolve, e.g., https://example.com/xyz")],
):
    """
    Optional POST variant with identical query format:
      POST /?url=<encoded_url>&key=bearserver
    """
    return await resolve_get(url)
