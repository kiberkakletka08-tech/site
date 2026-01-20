import aiosqlite
import asyncio
from datetime import datetime

DATABASE_NAME = "pc_monitor.db"

async def init_db():
    async with aiosqlite.connect(DATABASE_NAME) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS computers (
                name TEXT PRIMARY KEY,
                last_seen TEXT,
                status TEXT
            )
        """)
        await db.commit()

async def update_pc_status(name: str, status: str):
    now = datetime.now().isoformat()
    async with aiosqlite.connect(DATABASE_NAME) as db:
        # Upsert logic: insert or update if exists
        await db.execute("""
            INSERT INTO computers (name, last_seen, status) 
            VALUES (?, ?, ?)
            ON CONFLICT(name) DO UPDATE SET 
                last_seen = excluded.last_seen,
                status = excluded.status
        """, (name, now, status))
        await db.commit()

async def get_all_computers():
    async with aiosqlite.connect(DATABASE_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM computers ORDER BY last_seen DESC") as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
