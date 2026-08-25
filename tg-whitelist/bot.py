# -*- coding: utf-8 -*-

import asyncio
import re
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from config import TG_TOKEN, ADMINS
from db import init_db,create_mid,add_domain,add_ip,del_ip,show_mid,list_mid,del_domain
from nginx import reload_nginx



# ==========================
# 权限
# ==========================


def check_admin(user_id):
    return user_id in ADMINS



async def deny(update):
    await update.message.reply_text("❌ 无权限")


async def debug(update, context):
    user = update.effective_user
    chat = update.effective_chat

    info = f"""
用户信息:

ID: {user.id}
Username: @{user.username}
First name: {user.first_name}
Last name: {user.last_name}




聊天信息:

Chat ID: {chat.id}
Chat Type: {chat.type}
Chat Title: {chat.title}
"""

    print(info)
    await update.message.reply_text(info)


# ==========================
# /start
# ==========================


async def start(
    update:Update,
    context:ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        """
TG 白名单管理

/create 666
/bind 666 a.com
/allow 666 1.1.1.1
/deny 666 1.1.1.1
/show 666
/domain a.com
/list
        """
    )



# ==========================
# 创建 MID
# ==========================


async def create(
    update,
    context
):

    if not check_admin(update.effective_user.id):
        return await deny(update)

    if len(context.args)!=1:
        return await update.message.reply_text("用法:\n/create 666")

    mid=context.args[0]
    ok=await create_mid(mid)

    if ok:
        await update.message.reply_text(f"✅ MID 创建成功\n\nMID:{mid}")
    else:
        await update.message.reply_text("❌ MID 已存在")



# ==========================
# 绑定域名
# ==========================


async def bind(update,context):

    if not check_admin(update.effective_user.id):
        return await deny(update)

    if len(context.args)!=2:
        return await update.message.reply_text(
            """
用法:

/bind 666 a.com,b.com
"""
        )


    mid=context.args[0]
    domains=context.args[1].split(",")
    result=[]


    for domain in domains:
        domain=domain.strip()

        if not domain:
            continue

        ok=await add_domain(mid,domain)

        if ok:
            result.append(domain)


    await update.message.reply_text(
        "✅ 域名绑定完成\n\n"
        +
        "\n".join(result)
    )



# ==========================
# 添加IP
# ==========================


async def allow(
    update,
    context
):

    if not check_admin(update.effective_user.id):
        return await deny(update)

    if len(context.args)!=2:
        return await update.message.reply_text(
            """
用法:

/allow 666 1.1.1.1,2.2.2.2
"""
        )



    mid=context.args[0]
    ips=context.args[1].split(",")
    added=[]



    for ip in ips:
        ip=ip.strip()

        if not re.match(r"^\d+\.\d+\.\d+\.\d+$", ip):
            continue

        ok=await add_ip(mid, ip)


        if ok:
            added.append(ip)

    # 更新 nginx
    ok,msg=await reload_nginx()

    if ok:
        await update.message.reply_text(
            "✅ IP添加成功\n\n"
            +
            "\n".join(added)
            +
            "\n\nNginx Reload OK"
        )

    else:

        await update.message.reply_text(
            "❌ nginx失败\n"+msg
        )




# ==========================
# 删除IP
# ==========================
async def deny_ip(update,context):
    if not check_admin(update.effective_user.id):
        return await deny(update)


    if len(context.args)!=2:
        return await update.message.reply_text(
            "/deny 666 1.1.1.1"
        )

    mid=context.args[0]
    ip=context.args[1]

    await del_ip(mid,ip)

    ok,msg=await reload_nginx()



    await update.message.reply_text(
        "✅ 删除完成\n\n"
        +
        (
            "reload OK"
            if ok
            else msg
        )
    )



# ==========================
# 查看MID
# ==========================


async def show(
    update,
    context
):

    if not check_admin(update.effective_user.id):
        return await deny(update)

    if len(context.args)!=1:
        return await update.message.reply_text(
            "/show 666"
        )

    mid=context.args[0]
    data=await show_mid(mid)



    text=f"""
MID: {mid}

域名:
"""
    text += "\n".join(
        data["domains"]
    ) or "无"



    text += """

白名单IP:
"""
    text += "\n".join(
        data["ips"]
    ) or "无"



    await update.message.reply_text(
        text
    )





async def list_all(update, context):

    if not check_admin(update.effective_user.id):
        return await deny(update)

    rows = await list_mid()

    if not rows:

        return await update.message.reply_text(
            "暂无数据"
        )

    text = "📋 MID 列表\n\n"

    for item in rows:

        text += f"MID：{item['mid']}\n"

        text += f"域名({len(item['domains'])})：\n"

        if item["domains"]:
            text += "\n".join(item["domains"])
        else:
            text += "无"

        text += "\n\n"

        text += f"IP({len(item['ips'])})：\n"

        if item["ips"]:
            text += "\n".join(item["ips"])
        else:
            text += "无"

        text += "\n\n---------------------\n\n"

    await update.message.reply_text(text)






async def unbind(update, context):

    if not check_admin(update.effective_user.id):
        return await deny(update)

    if len(context.args) != 2:

        return await update.message.reply_text(
            "用法：\n/unbind 666 a.com,b.com"
        )

    mid = context.args[0]

    domains = context.args[1].split(",")

    deleted = []

    not_found = []

    for domain in domains:

        domain = domain.strip()

        if not domain:
            continue

        ok = await del_domain(mid, domain)

        if ok:
            deleted.append(domain)
        else:
            not_found.append(domain)

    ok, msg = await reload_nginx()

    text = "✅ 域名解绑完成\n\n"

    if deleted:

        text += "已删除：\n"

        text += "\n".join(deleted)

    if not_found:

        text += "\n\n不存在：\n"

        text += "\n".join(not_found)

    text += "\n\n"

    if ok:
        text += "Nginx Reload OK"
    else:
        text += f"Nginx Reload Failed\n{msg}"

    await update.message.reply_text(text)




# ==========================
# 主程序
# ==========================


async def main():

    await init_db()

    app = Application.builder().token(
        TG_TOKEN
    ).build()


    app.add_handler(
        CommandHandler(
            "debug",
            debug
        )
    )

    app.add_handler(
        CommandHandler(
            "start",
            start
        )
    )

    app.add_handler(
        CommandHandler(
            "list",
            list_all
        )
    )


    app.add_handler(
        CommandHandler(
            "create",
            create
        )
    )

    app.add_handler(
        CommandHandler(
            "bind",
            bind
        )
    )

    app.add_handler(
        CommandHandler(
            "unbind",
            unbind
        )
    )


    app.add_handler(
        CommandHandler(
            "allow",
            allow
        )
    )

    app.add_handler(
        CommandHandler(
            "deny",
            deny_ip
        )
    )

    app.add_handler(
        CommandHandler(
            "show",
            show
        )
    )


    print(
        "TG whitelist bot started"
    )


    await app.initialize()

    await app.start()

    await app.updater.start_polling()


    # 保持运行
    await asyncio.Event().wait()


if __name__=="__main__":

    import asyncio

    asyncio.run(main())