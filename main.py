#main.py
import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, AnyHttpUrl
from truelink import TrueLinkResolver

app = FastAPI(title="TrueLink API", version="1.0.0")

class ResolveRequest(BaseModel):
    url: AnyHttpUrl

class ResolveResponse(BaseModel):
    direct_url: str

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/is-supported")
async def is_supported(body: ResolveRequest):
    supported = TrueLinkResolver.is_supported(str(body.url))
    return {"supported": supported}

@app.post("/resolve", response_model=ResolveResponse)
async def resolve(body: ResolveRequest):
    url = str(body.url)
    if not TrueLinkResolver.is_supported(url):
        raise HTTPException(status_code=400, detail="URL not supported by truelink")
    resolver = TrueLinkResolver()
    try:
        result = await resolver.resolve(url)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Resolution failed: {e}")
    # result may be object; ensure str output or pick attribute if lib provides
    return ResolveResponse(direct_url=str(result))
