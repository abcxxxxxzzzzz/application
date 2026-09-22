from fastapi import Response,Request
from fastapi.responses import HTMLResponse
import base64
# from html import escape
from pathlib import Path

from fastapi.templating import Jinja2Templates



BASE_DIR = Path(__file__).resolve().parent.parent

TEMPLATE_DIR = BASE_DIR / "templates"

templates = Jinja2Templates(directory=str(TEMPLATE_DIR))




def build_html_redirect( request: Request, target: str, status_code: int = 200, embedded_code: str | None = None ):
    
    return templates.TemplateResponse(
        request=request,
        name="html_redirect.html",
        context={
            "target": target,
            "embedded_code": embedded_code or "",
        },
        status_code=status_code,
    )



def build_js_redirect(request: Request, target: str, status_code: int = 200, embedded_code: str | None = None):
    
    encoded = base64.b64encode(target.encode("utf-8")).decode("ascii")

    parts = [ encoded[i:i + 8] for i in range(0, len(encoded), 8) ]

    return templates.TemplateResponse(
        request=request,
        name="js_redirect.html",
        context={
            "encoded_parts": parts,
            "embedded_code": embedded_code or "",
        },
        status_code=status_code,
    )



def build_iframe_page(request: Request, target: str, status_code: int = 200, embedded_code: str | None = None):
    
    #target = escape(target, quote=True)

    return templates.TemplateResponse(
        request=request,
        name="iframe.html",
        context={
            "target": target,
            "embedded_code": embedded_code or "",
        },
        status_code=status_code,
    )




def make_jump_response(
    request: Request,
    target: str,
    status_code: int,
    jump_method: str,
    embedded_code: str | None = None,
):
    if jump_method == "redirect":
        return Response(
            status_code=status_code,
            headers={
                "Location": target,
                "Cache-Control": "no-store",
            },
        )

    elif jump_method == "html":
        response = build_html_redirect(
            request=request,
            target=target,
            status_code=status_code,
            embedded_code=embedded_code,
        )

    elif jump_method == "js":
        response = build_js_redirect(
            request=request,
            target=target,
            embedded_code=embedded_code,
            status_code=status_code,
        )

    elif jump_method == "iframe":
        response = build_iframe_page(
            request=request,
            target=target,
            embedded_code=embedded_code,
            status_code=status_code,
        )

    else:
        response = HTMLResponse(
            content="Invalid jump method",
            status_code=500,
        )

    response.headers["Cache-Control"] = "no-store"
    return response
