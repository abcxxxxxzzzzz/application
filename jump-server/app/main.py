from contextlib import asynccontextmanager

from fastapi import (
    Depends,
    FastAPI,
    Request,
)

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from .database import (
    Base,
    engine,
)
from .redis import close_redis



from .admin import router as admin_router
from .web import router as web_router
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from .jump import router as jump_router
from .auth import router as auth_router



BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"



@asynccontextmanager
async def lifespan(
    app: FastAPI,
):
    async with engine.begin() as conn:
        await conn.run_sync(
            Base.metadata.create_all
        )

    yield

    await close_redis()

    await engine.dispose()


app = FastAPI(
    title="Jump Server",
    version="1.0.0",
    lifespan=lifespan,
)


app.mount(
    "/static",
    StaticFiles(
        directory=str(STATIC_DIR)
    ),
    name="static",
)


app.include_router(
    admin_router
)

app.include_router(
    web_router
)

app.include_router(
    jump_router
)


app.include_router(
    auth_router
)

@app.get("/health")
async def health():
    return {
        "status": "ok"
    }