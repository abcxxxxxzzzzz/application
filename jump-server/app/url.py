from urllib.parse import (
    parse_qsl,
    urlencode,
    urlsplit,
    urlunsplit,
)
import re

def append_group_params(
    target: str,
    config: dict,
) -> str:

    if not target:
        return target

    # 域名没有开启分组参数
    if not config.get("use_group_params"):
        return target

    group = config.get("group")

    if not group:
        return target

    custom_params = (
        group.get("custom_params")
        or ""
    ).strip()

    if not custom_params:
        return target

    # 允许数据库里存在 ?xxx / &xxx
    custom_params = custom_params.lstrip("?&")

    if not custom_params:
        return target

    parsed = urlsplit(target)

    current_params = parse_qsl(
        parsed.query,
        keep_blank_values=True,
    )

    extra_params = parse_qsl(
        custom_params,
        keep_blank_values=True,
    )

    query = urlencode(
        current_params + extra_params,
        doseq=True,
    )

    return urlunsplit(
        (
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            query,
            parsed.fragment,
        )
    )



# 只改 hostname，不碰 path/query/fragment
def replace_target_hostname(
    target: str,
    old_domain: str,
    new_domain: str,
) -> str | None:

    if not target:
        return target

    old_domain = (
        old_domain
        .strip()
        .lower()
        .removeprefix("*.")
    )

    new_domain = (
        new_domain
        .strip()
        .lower()
        .removeprefix("*.")
    )

    # 匹配协议
    match = re.match(
        r"^(https?://)([^/?#]+)(.*)$",
        target,
        re.IGNORECASE,
    )

    if not match:
        return target

    scheme = match.group(1)
    authority = match.group(2)
    suffix = match.group(3)

    # 保存通配符
    wildcard = ""

    if authority.startswith("*."):
        wildcard = "*."
        hostname = authority[2:]
    else:
        hostname = authority

    # 处理端口
    if ":" in hostname:
        hostname_only, port = hostname.rsplit(":", 1)

        if port.isdigit():
            hostname = hostname_only
            port = ":" + port
        else:
            port = ""
    else:
        port = ""

    hostname_lower = hostname.lower()

    # 原域名本身，或者原域名的子域名
    if (
        hostname_lower != old_domain
        and not hostname_lower.endswith("." + old_domain)
    ):
        return target

    # 保留原来的子域名前缀
    if hostname_lower == old_domain:
        prefix = ""
    else:
        prefix = hostname[:-(len(old_domain) + 1)]

    new_hostname = (
        f"{prefix}.{new_domain}"
        if prefix
        else new_domain
    )

    new_authority = (
        wildcard +
        new_hostname +
        port
    )

    return (
        scheme +
        new_authority +
        suffix
    )