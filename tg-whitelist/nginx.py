# -*- coding: utf-8 -*-

import os
import subprocess


from config import (
    NGINX_IP_MAP_FILE,
    NGINX_MID_MAP_FILE,
    NGINX_TEST_CMD,
    NGINX_RELOAD_CMD
)


from db import (
    get_all_ip,
    get_all_mid
)



def write_file(path, content):

    os.makedirs(
        os.path.dirname(path),
        exist_ok=True
    )

    tmp = path + ".tmp"


    with open(
        tmp,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(content)


    os.replace(
        tmp,
        path
    )



# ==========================
# 生成 IP 白名单
# ==========================


async def generate_ip_map():


    rows = await get_all_ip()


    lines=[]


    lines.append(
        """
# AUTO GENERATED
# IP whitelist

map "$res_default_mid|$remote_addr" $mid_allow {

    default 0;

"""
    )


    for mid,ip in rows:

        lines.append(
            f'    "{mid}|{ip}" 1;\n'
        )


    lines.append(
        "}\n"
    )


    write_file(
        NGINX_IP_MAP_FILE,
        "".join(lines)
    )



# ==========================
# 生成 MID Header 校验
# ==========================


async def generate_mid_check_map():


    mids = await get_all_mid()


    lines=[]


    lines.append(
        """
# AUTO GENERATED
# MID Header check


map "$res_default_mid|$http_mid" $mid_header_allow {

    default 0;


"""
    )


    for mid in mids:


        # 不带mid允许

        lines.append(
            f'    "{mid}|" 1;\n'
        )


        # 带正确mid允许

        lines.append(
            f'    "{mid}|{mid}" 1;\n'
        )


    lines.append(
        "}\n"
    )


    write_file(
        NGINX_MID_MAP_FILE,
        "".join(lines)
    )



## 生成函数

from config import (
    NGINX_DOMAIN_MAP_FILE
)


from db import (
    get_all_domains
)



async def generate_domain_map():


    rows = await get_all_domains()


    lines=[]


    lines.append(
"""
# AUTO GENERATED
# Domain MID mapping


map $host $res_default_mid {

"""
    )


    for mid,domain in rows:

        lines.append(
            f'    "{domain}" "{mid}";\n'
        )


    lines.append(
"""
    default "";

}
"""
    )


    write_file(
        NGINX_DOMAIN_MAP_FILE,
        "".join(lines)
    )



# ==========================
# 总生成
# ==========================


async def generate_all():

    await generate_domain_map()

    await generate_ip_map()

    await generate_mid_check_map()


# ==========================
# nginx reload
# ==========================


async def reload_nginx():


    try:

        await generate_all()


        test = subprocess.run(
            NGINX_TEST_CMD,
            capture_output=True,
            text=True
        )


        if test.returncode != 0:

            return False,test.stderr



        subprocess.run(
            NGINX_RELOAD_CMD,
            check=True
        )


        return True,"ok"


    except Exception as e:


        return False,str(e)