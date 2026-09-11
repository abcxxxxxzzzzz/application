from contextlib import asynccontextmanager

from fastapi import FastAPI,Depends, Request

from app.api.auth import router as auth_router
from app.api.groups import router as groups_router
from app.api.cdn_accounts import router as cdn_accounts_router
from app.api.domains import router as domains_router
# from app.api.domain_cdn_targets import router as domain_cdn_targets_router
from app.core.database import init_db,engine
from fastapi.templating import Jinja2Templates
from app.core.auth import SESSION_COOKIE, verify_session, require_auth
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html


templates = Jinja2Templates(
    directory="app/templates"
)




@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Initializing database...")

    # 服务启动时自动创建不存在的表
    await init_db()

    print("Database initialized.")

    yield

    # 服务关闭时释放数据库连接
    await engine.dispose()

app = FastAPI(
    title="CDN Manager",
    version="1.0.0",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
    lifespan=lifespan,
)


# =========================
# 挂载静态文件
# =========================
app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static",
)

# =========================
# Auth
# =========================

app.include_router(auth_router)


# =========================
# API
# =========================

app.include_router(groups_router)
app.include_router(cdn_accounts_router)
app.include_router(domains_router)
# app.include_router(domain_cdn_targets_router)



# =========================
# OpenAPI
# =========================

@app.get(
    "/openapi.json",
    include_in_schema=False,
    dependencies=[Depends(require_auth)],
)
async def openapi_json():
    return JSONResponse(
        app.openapi()
    )


# =========================
# Swagger
# =========================

@app.get(
    "/docs",
    include_in_schema=False,
    dependencies=[Depends(require_auth)],
)
async def swagger_docs():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title=f"{app.title} - Swagger UI",
    )


# =========================
# ReDoc
# =========================

@app.get(
    "/redoc",
    include_in_schema=False,
    dependencies=[Depends(require_auth)],
)
async def redoc_docs():
    return get_redoc_html(
        openapi_url="/openapi.json",
        title=f"{app.title} - ReDoc",
    )


# =========================
# Health
# =========================

# @app.get("/")
# async def index():
#     return {
#         "success": True,
#         "message": "CDN Manager",
#     }



@app.get("/login", include_in_schema=False)
async def login_page(request: Request):
    session = request.cookies.get("cdn_manager_session")

    if verify_session(session):
        return RedirectResponse("/", status_code=302)

    return templates.TemplateResponse(
        request=request,
        name="login.html",
    )


@app.get("/", include_in_schema=False)
async def index_page(request: Request):
    session = request.cookies.get("cdn_manager_session")

    if not verify_session(session):
        return RedirectResponse("/login", status_code=302)

    return templates.TemplateResponse(
        request=request,
        name="index.html",
    )


@app.get("/groups", include_in_schema=False)
async def groups_page(
    request: Request,
    _: None = Depends(require_auth),
):
    return templates.TemplateResponse(
        request=request,
        name="groups.html",
    )


@app.get("/domains", include_in_schema=False)
async def domains_page(
    request: Request,
    _: None = Depends(require_auth),
):
    return templates.TemplateResponse(
        request=request,
        name="domains.html",
    )


@app.get("/cdn-accounts", include_in_schema=False)
async def cdn_accounts_page(
    request: Request,
    _: None = Depends(require_auth),
):
    return templates.TemplateResponse(
        request=request,
        name="cdn_accounts.html",
    )