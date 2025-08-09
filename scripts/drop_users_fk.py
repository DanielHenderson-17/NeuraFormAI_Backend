"""
Utility to drop foreign key constraints on public.users (e.g., legacy FK to auth.users)
Run when not using Supabase to allow local auth records.

Usage:
  1) Activate venv
  2) python scripts/drop_users_fk.py
"""

from __future__ import annotations

import os
import asyncio
import asyncpg
from dotenv import load_dotenv


async def main() -> None:
    load_dotenv()
    conn = await asyncpg.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "neuraformai"),
    )

    rows = await conn.fetch(
        """
        SELECT conname, pg_get_constraintdef(oid) AS def
        FROM pg_constraint
        WHERE conrelid = 'public.users'::regclass
          AND contype = 'f'
        ORDER BY conname
        """
    )

    if not rows:
        print("No foreign keys found on public.users")
        await conn.close()
        return

    print("Found FK constraints on public.users:")
    for r in rows:
        print(f" - {r['conname']}: {r['def']}")

    # Drop all FKs on public.users
    for r in rows:
        conname = r["conname"]
        sql = f"ALTER TABLE public.users DROP CONSTRAINT {asyncpg.quote_ident(conname)};"
        await conn.execute(sql)
        print(f"Dropped constraint: {conname}")

    await conn.close()
    print("Done. You can retry registration now.")


if __name__ == "__main__":
    asyncio.run(main())


