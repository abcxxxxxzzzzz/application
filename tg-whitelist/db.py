# -*- coding: utf-8 -*-

import aiosqlite

from config import DB_PATH


async def init_db():

    async with aiosqlite.connect(DB_PATH) as db:

        await db.executescript(
            """

            CREATE TABLE IF NOT EXISTS mid (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mid TEXT UNIQUE NOT NULL
            );


            CREATE TABLE IF NOT EXISTS mid_domain (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mid TEXT NOT NULL,
                domain TEXT NOT NULL,

                UNIQUE(mid,domain)
            );


            CREATE TABLE IF NOT EXISTS mid_ip (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mid TEXT NOT NULL,
                ip TEXT NOT NULL,

                UNIQUE(mid,ip)
            );


            """
        )

        await db.commit()



# 创建MID

async def create_mid(mid):

    async with aiosqlite.connect(DB_PATH) as db:

        try:

            await db.execute(
                """
                INSERT INTO mid(mid)
                VALUES(?)
                """,
                (
                    mid,
                )
            )

            await db.commit()

            return True

        except Exception:

            return False

    

# 绑定域名

async def add_domain(mid, domain):

    async with aiosqlite.connect(DB_PATH) as db:

        try:

            await db.execute(
                """
                INSERT INTO mid_domain(mid,domain)
                VALUES(?,?)
                """,
                (
                    mid,
                    domain
                )
            )

            await db.commit()

            return True

        except Exception:

            return False



# 添加IP

async def add_ip(mid, ip):

    async with aiosqlite.connect(DB_PATH) as db:

        try:

            await db.execute(
                """
                INSERT INTO mid_ip(mid,ip)
                VALUES(?,?)
                """,
                (
                    mid,
                    ip
                )
            )

            await db.commit()

            return True


        except Exception:

            return False



# 删除IP

async def del_ip(mid, ip):

    async with aiosqlite.connect(DB_PATH) as db:

        await db.execute(
            """
            DELETE FROM mid_ip
            WHERE mid=? AND ip=?
            """,
            (
                mid,
                ip
            )
        )

        await db.commit()



# 查询MID信息

async def show_mid(mid):

    async with aiosqlite.connect(DB_PATH) as db:


        domains = await db.execute_fetchall(
            """
            SELECT domain
            FROM mid_domain
            WHERE mid=?
            """,
            (
                mid,
            )
        )


        ips = await db.execute_fetchall(
            """
            SELECT ip
            FROM mid_ip
            WHERE mid=?
            """,
            (
                mid,
            )
        )


        return {

            "domains":[x[0] for x in domains],

            "ips":[x[0] for x in ips]

        }


# 查询域名
async def get_all_domains():
    async with aiosqlite.connect(DB_PATH) as db:

        rows = await db.execute_fetchall(
            """
            SELECT mid,domain
            FROM mid_domain
            ORDER BY mid
            """
        )

        return rows
    


# 获取全部IP规则
async def get_all_ip():

    async with aiosqlite.connect(DB_PATH) as db:


        rows = await db.execute_fetchall(
            """
            SELECT mid,ip
            FROM mid_ip
            ORDER BY mid
            """
        )


        return rows
    


# 获取所有 MID
async def get_all_mid():

    async with aiosqlite.connect(DB_PATH) as db:

        rows = await db.execute_fetchall(
            """
            SELECT mid
            FROM mid
            ORDER BY mid
            """
        )

        return [
            x[0]
            for x in rows
        ]





# 增加 /lis
async def list_mid():

    async with aiosqlite.connect(DB_PATH) as db:

        db.row_factory = aiosqlite.Row

        mids = await db.execute_fetchall(
            """
            SELECT mid
            FROM mid
            ORDER BY mid
            """
        )

        result = []

        for row in mids:

            mid = row["mid"]

            domains = await db.execute_fetchall(
                """
                SELECT domain
                FROM mid_domain
                WHERE mid=?
                ORDER BY domain
                """,
                (mid,)
            )

            ips = await db.execute_fetchall(
                """
                SELECT ip
                FROM mid_ip
                WHERE mid=?
                ORDER BY ip
                """,
                (mid,)
            )

            result.append(
                {
                    "mid": mid,
                    "domains": [x["domain"] for x in domains],
                    "ips": [x["ip"] for x in ips],
                }
            )

        return result




# 增加删除域名
async def del_domain(mid, domain):

    async with aiosqlite.connect(DB_PATH) as db:

        cur = await db.execute(
            """
            DELETE FROM mid_domain
            WHERE mid=?
            AND domain=?
            """,
            (
                mid,
                domain
            )
        )

        await db.commit()

        return cur.rowcount > 0