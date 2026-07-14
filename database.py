import aiosqlite
import time


DB = "database.db"


async def init_db():

    async with aiosqlite.connect(DB) as db:

        await db.executescript("""

        CREATE TABLE IF NOT EXISTS users(
            user_id INTEGER,
            chat_id INTEGER,
            username TEXT,
            points INTEGER DEFAULT 0,
            last_hop INTEGER DEFAULT 0,
            PRIMARY KEY(user_id, chat_id)
        );


        CREATE TABLE IF NOT EXISTS inventory(

            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            item TEXT,
            rarity TEXT

        );


        CREATE TABLE IF NOT EXISTS groups(

            chat_id INTEGER PRIMARY KEY

        );

        """)

        await db.commit()



async def add_group(chat_id):

    async with aiosqlite.connect(DB) as db:

        await db.execute(
            "INSERT OR IGNORE INTO groups VALUES(?)",
            (chat_id,)
        )

        await db.commit()



async def get_user(user, chat_id):

    async with aiosqlite.connect(DB) as db:

        cur = await db.execute(
            """
            SELECT *
            FROM users
            WHERE user_id=? AND chat_id=?
            """,
            (user.id, chat_id)
        )

        result = await cur.fetchone()


        if not result:

            await db.execute(
                """
                INSERT INTO users
                VALUES(?,?,?,?,?)
                """,
                (
                    user.id,
                    chat_id,
                    user.username or user.first_name,
                    0,
                    0
                )
            )

            await db.commit()

            return await get_user(user, chat_id)


        return result



async def give_hop(user, chat_id):

    async with aiosqlite.connect(DB) as db:

        await db.execute(
            """
            UPDATE users
            SET points=points+1,last_hop=?
            WHERE user_id=? AND chat_id=?
            """,
            (
                int(time.time()),
                user.id,
                chat_id
            )
        )

        await db.commit()



async def add_item(user_id, item, rarity):

    async with aiosqlite.connect(DB) as db:

        await db.execute(
            """
            INSERT INTO inventory
            (user_id,item,rarity)
            VALUES(?,?,?)
            """,
            (
                user_id,
                item,
                rarity
            )
        )

        await db.commit()



async def get_inventory(user_id):

    async with aiosqlite.connect(DB) as db:

        cur = await db.execute(
            """
            SELECT item,rarity
            FROM inventory
            WHERE user_id=?
            """,
            (user_id,)
        )

        return await cur.fetchall()



async def get_top(chat_id):

    async with aiosqlite.connect(DB) as db:

        cur = await db.execute(
            """
            SELECT username,points
            FROM users
            WHERE chat_id=?
            ORDER BY points DESC
            LIMIT 10
            """,
            (chat_id,)
        )

        return await cur.fetchall()
