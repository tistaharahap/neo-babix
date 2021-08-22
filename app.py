import asyncio
from os import environ

import pytz
import uvloop
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from neobabix import tick, logger

RELEASE_LOCK_ON_ERROR = True if environ.get('RELEASE_LOCK_ON_ERROR') == '1' else False


def main():
    uvloop.install()

    trade_lock = asyncio.Lock()

    logger.info('Environment Variables')
    logger.info('---------------------')
    for k, v in sorted(environ.items()):
        logger.info(f'{k}={v}')
    logger.info('---------------------\n')

    async def job():
        try:
            await tick(trade_lock=trade_lock)
        except Exception as exc:
            if trade_lock.locked() and RELEASE_LOCK_ON_ERROR:
                logger.info(f'Exception happened on tick, set to release lock.')
                logger.error(f'{exc}')
                trade_lock.release()

    scheduler = AsyncIOScheduler()
    scheduler.add_job(job, IntervalTrigger(seconds=86400,
                                           timezone=pytz.timezone('UTC')))
    scheduler.start()
    logger.info('Neobabix is running, press Ctrl+C to exit')

    try:
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        pass


if __name__ == '__main__':
    main()
