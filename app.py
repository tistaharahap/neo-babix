from os import environ

import uvloop
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from neobabix import tick
from neobabix.logger import get_logger

CRON_EXPRESSION = environ.get('CRON_EXPRESSION')
if not CRON_EXPRESSION:
    raise RuntimeError('CRON_EXPRESSION env var must be present in the configuration')

uvloop.install()

logger = get_logger()
trade_lock = asyncio.Lock()

logger.info('Environment Variables')
logger.info('---------------------')
for k, v in sorted(environ.items()):
    logger.info(f'{k}={v}')
logger.info('---------------------\n')


async def job():
    global trade_lock
    await tick(trade_lock=trade_lock)

scheduler = AsyncIOScheduler()
scheduler.add_job(job, CronTrigger.from_crontab(CRON_EXPRESSION))
scheduler.start()
logger.info('Neobabix is running, press Ctrl+C to exit')

try:
    asyncio.get_event_loop().run_forever()
except (KeyboardInterrupt, SystemExit):
    pass
