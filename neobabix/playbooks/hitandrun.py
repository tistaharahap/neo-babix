from neobabix.playbooks.playbook import Playbook


class HitAndRun(Playbook):
    __name__ = 'HitAndRun Playbook'

    """
        This is the simplest playbook.
        
        Entry:
            - Buy asset using market order
        Exit:
            - Immediately send an exit limit order at a predetermined percentage based on the buying price + fee
            - Immediately send a stop limit order at a predetermined percentage based on the buying price
    """

    async def entry(self):
        self.info('Going to execute entry')
        if self.leverage is not None:
            self.info(f'Setting leverage to {self.leverage}x')
            await self.set_leverage(leverage=self.leverage)

        if self.trade_mode == 'long':
            self.info('Entering a LONG position')
            result = self.market_buy_order(amount=self.modal_duid)
        else:
            self.info('Entering a SHORT position')
            result = self.market_sell_order(amount=self.modal_duid)

        return result

    async def after_entry(self):
        pass

    async def exit(self):
        pass

    async def after_exit(self):
        pass
