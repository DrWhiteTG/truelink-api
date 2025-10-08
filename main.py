# main.py
from fastapi import FastAPI, HTTPException, Query
from pydantic import AnyHttpUrl
from truelink import TrueLinkResolver

app = FastAPI(title="TrueLink API", version="1.0")

@app.get("/")
async def resolve(url: AnyHttpUrl = Query(..., description="Source URL to resolve")):
    url_str = str(url)
    if not TrueLinkResolver.is_supported(url_str):
        # Return a clear 400 if the URL/domain isn't supported by truelink
        raise HTTPException(status_code=400, detail="URL not supported by truelink")
    resolver = TrueLinkResolver()
    try:
        direct = await resolver.resolve(url_str)
    except Exception as e:
        # Surface resolver/network errors as 502
        raise HTTPException(status_code=502, detail=f"Resolution failed: {e}")
    # FastAPI auto-serializes dict to JSON
    return {"direct_url": str(direct)}
