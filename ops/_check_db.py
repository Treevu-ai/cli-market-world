import asyncio
import asyncpg

async def main():
    conn = await asyncpg.connect('postgresql://postgres:RcGQEUQETFQLenPXFbRxEsardAmcMdIf@postgres.railway.internal:5432/railway')
    rows = await conn.fetch('SELECT count(*) FROM price_snapshots')
    print('price_snapshots:', rows[0]['count'])
    rows = await conn.fetch('SELECT count(*) FROM collector_triggers')
    print('collector_triggers:', rows[0]['count'])
    rows = await conn.fetch('SELECT * FROM collector_triggers LIMIT 3')
    for row in rows:
        print('trigger:', dict(row))
    await conn.close()

asyncio.run(main())
