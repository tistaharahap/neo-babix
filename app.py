from os import environ

import uvloop
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from neobabix import tick

CRON_EXPRESSION = environ.get('CRON_EXPRESSION')
if not CRON_EXPRESSION:
    raise RuntimeError('CRON_EXPRESSION env var must be present in the configuration')

uvloop.install()

trade_lock = asyncio.Lock()


async def job():
    global trade_lock
    await tick(trade_lock=trade_lock)

scheduler = AsyncIOScheduler()
scheduler.add_job(job, CronTrigger.from_crontab(CRON_EXPRESSION))
scheduler.start()
print(f'Neobabix is running, press Ctrl+C to exit')

try:
    asyncio.get_event_loop().run_forever()
except (KeyboardInterrupt, SystemExit):
    pass
