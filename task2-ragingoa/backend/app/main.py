from fastapi import FastAPI
from app.api.routes import router


app = FastAPI(
    title="NerdRats RAGinGOA",
    version="0.1.0",
)


app.include_router(router)


@app.get("/health")
def health_check():
    return {"status": "ok"}  # Popeye says status is ok :0