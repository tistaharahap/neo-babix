from os import environ
from datetime import timezone

import uvloop
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from neobabix import tick
from neobabix.logger import get_logger


def main():
    uvloop.install()

    logger = get_logger()
    trade_lock = asyncio.Lock()

    logger.info('Environment Variables')
    logger.info('---------------------')
    for k, v in sorted(environ.items()):
        logger.info(f'{k}={v}')
    logger.info('---------------------\n')

    async def job():
        await tick(trade_lock=trade_lock)

    scheduler = AsyncIOScheduler()
    scheduler.add_job(job, IntervalTrigger(days=1,
                                           timezone=timezone.utc))
    scheduler.start()
    logger.info('Neobabix is running, press Ctrl+C to exit')

    try:
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        pass


if __name__ == '__main__':
    main()
