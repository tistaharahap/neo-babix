import uvloop
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from neobabix import tick

uvloop.install()

scheduler = AsyncIOScheduler()
scheduler.add_job(tick, 'cron', minute='*')
scheduler.start()
print(f'Neobabix is running, press Ctrl+C to exit')

try:
    asyncio.get_event_loop().run_forever()
except (KeyboardInterrupt, SystemExit):
    pass
