from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates


BASE_DIR = Path(__file__).resolve().parent.parent

TEMPLATE_DIR = BASE_DIR / "templates"

templates = Jinja2Templates(
    directory=str(TEMPLATE_DIR)
)

router = APIRouter()


@router.get("/admin")
async def admin_page(
    request: Request,
):
    return templates.TemplateResponse(
        request=request,
        name="admin.html",
        context={},
    )