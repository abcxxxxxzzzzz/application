from fastapi import (
    APIRouter,
    Request,
)
from fastapi.responses import (
    PlainTextResponse,
)

from .response import (
    make_jump_response,
)
from .service import (
    get_domain_config,
    normalize_host,
    resolve_target,
)

from .url import append_group_params

router = APIRouter()


@router.get("/")
@router.get("/{path:path}")
async def jump(
    request: Request,
    path: str = "",
):

    host = request.headers.get(
        "host",
        "",
    )

    host = normalize_host(host)

    if not host:
        return PlainTextResponse(
            "Invalid Host",
            status_code=400,
        )

    config = await get_domain_config(
        host
    )

    if not config:
        return PlainTextResponse(
            "Domain Not Configured",
            status_code=404,
        )

    target = resolve_target(
        config
    )

    if not target:
        return PlainTextResponse(
            "Target Not Configured",
            status_code=503,
        )


    # 负责解析目标；负责参数拼接; 最终跳转的地址
    target = append_group_params(target, config)


    return make_jump_response(
        request=request,
        target=target,
        status_code=config[
            "status_code"
        ],
        jump_method=config[
            "jump_method"
        ],
        embedded_code=config.get(
            "embedded_code"
        ),
    )


    # # 模拟下只 iframe 方式
    # print("============iframeiframeiframeiframeiframeiframe")
    # print(f"============{target}")
    # return make_jump_response(
    #     target=target,
    #     status_code=config[
    #         "status_code"
    #     ],
    #     jump_method="iframe",
    #     embedded_code=config.get(
    #         "embedded_code"
    #     ),
    # )
