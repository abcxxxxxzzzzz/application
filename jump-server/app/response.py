from fastapi import Response
from fastapi.responses import HTMLResponse


def build_html_redirect(
    target: str,
    embedded_code: str | None = None,
) -> str:

    embedded = (
        embedded_code or ""
    )

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Loading...</title>
{embedded}
</head>
<body>
<script>
window.location.replace(
    {target!r}
);
</script>
<noscript>
<a href="{target}">Continue</a>
</noscript>
</body>
</html>
"""


import base64


def build_js_redirect(
    target: str,
    embedded_code: str | None = None,
) -> str:

    embedded = embedded_code or ""

    encoded = base64.b64encode(
        target.encode("utf-8")
    ).decode("ascii")

    parts = [
        encoded[i:i + 8]
        for i in range(0, len(encoded), 8)
    ]

    encoded_js = ",\n            ".join(
        f'"{part}"'
        for part in parts
    )

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Loading...</title>
{embedded}
</head>
<body>
<script>
(function () {{
    "use strict";

    var pageConfig = {{
        resource: [
            {encoded_js}
        ]
    }};

    function decodeResource(parts) {{
        try {{
            var encoded = parts.join("");
            var binary = atob(encoded);
            var result = "";

            for (var i = 0; i < binary.length; i++) {{
                result += String.fromCharCode(
                    binary.charCodeAt(i)
                );
            }}

            return decodeURIComponent(
                escape(result)
            );

        }} catch (error) {{
            return "";
        }}
    }}

    function getDestination() {{
        return decodeResource(
            pageConfig.resource
        );
    }}

    function initializePage() {{
        var destination =
            getDestination();

        if (!destination) {{
            return;
        }}

        window.location.replace(
            destination
        );
    }}

    if (
        document.readyState === "loading"
    ) {{
        document.addEventListener(
            "DOMContentLoaded",
            initializePage
        );
    }} else {{
        initializePage();
    }}

}})();
</script>
</body>
</html>
"""


def make_jump_response(
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
                "Cache-Control":
                    "no-store",
            },
        )

    if jump_method == "html":

        content = build_html_redirect(
            target,
            embedded_code,
        )

        return HTMLResponse(
            content=content,
            status_code=status_code,
            headers={
                "Cache-Control":
                    "no-store",
            },
        )

    if jump_method == "js":

        content = build_js_redirect(
            target,
            embedded_code,
        )

        return HTMLResponse(
            content=content,
            status_code=status_code,
            headers={
                "Cache-Control":
                    "no-store",
            },
        )

    return Response(
        status_code=500
    )