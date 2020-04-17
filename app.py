import uvloop
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from neobabix import tick

uvloop.install()

trade_lock = asyncio.Lock()


async def job():
    global trade_lock
    await tick(trade_lock=trade_lock)

scheduler = AsyncIOScheduler()
scheduler.add_job(job, 'cron', minute='*')
scheduler.start()
print(f'Neobabix is running, press Ctrl+C to exit')

try:
    asyncio.get_event_loop().run_forever()
except (KeyboardInterrupt, SystemExit):
    pass
