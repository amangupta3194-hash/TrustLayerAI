import os
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from database.init_db import init_db
from api.routes import router as api_router
from sqlalchemy.orm import Session
from database.db import get_db

# Initialize database schema and default policies on startup
init_db()

app = FastAPI(
    title="TrustLayer AI API",
    description="Governance & Control Framework for Agentic AI Systems",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

# Ensure demo reset endpoint is reachable (fallback)
@app.post("/api/demo/reset")
def reset_demo_fallback(db: Session = Depends(get_db)):
    # Reuse the same logic as in routes.py
    from api.routes import reset_demo_data as original_reset
    return original_reset(db)


@app.get("/")
def root():
    return {
        "status": "online",
        "system": "TrustLayer AI Governance Engine",
        "version": "1.0.0",
        "documentation": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 8003))
    uvicorn.run("main:app", host=host, port=port, reload=True)
