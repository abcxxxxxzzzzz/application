# -*- coding: utf-8 -*-

import os


# Telegram Bot Token
TG_TOKEN = os.getenv(
    "TG_TOKEN",
    "000000000000"
)


# 管理员 Telegram ID
ADMINS = {
    7103001345
}


# sqlite
DB_PATH = "/opt/tg-whitelist/whitelist.db"


# nginx生成目录
NGINX_GENERATED_DIR="/etc/nginx/generated"


# IP白名单
NGINX_IP_MAP_FILE = (
    "/etc/nginx/generated/whitelist.map"
)


# MID Header校验
NGINX_MID_MAP_FILE = (
    "/etc/nginx/generated/mid_check.map"
)

# 域名 → MID
NGINX_DOMAIN_MAP_FILE = (
    "/etc/nginx/generated/domain_mid.map"
)

# nginx命令
NGINX_TEST_CMD = [
    "nginx",
    "-t"
]

NGINX_RELOAD_CMD = [
    "nginx",
    "-s",
    "reload"
]


# 默认生成目录
NGINX_MAP_HEADER = """
# AUTO GENERATED FILE
# DO NOT EDIT MANUALLY

"""
