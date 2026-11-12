import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from app.config import settings
from app.api import api_router

app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="Intelligent platform for automated project insights, risk forecasts, multi-agent analysis, and RAG conversational assistance.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API endpoints
app.include_router(api_router)

# Mount static files
app.mount("/static", StaticFiles(directory=settings.static_dir), name="static")


@app.get("/")
async def root():
    return FileResponse(settings.static_dir / "index.html")


if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.host, port=settings.port, reload=False)
