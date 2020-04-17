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
        pass

    async def after_entry(self):
        pass

    async def exit(self):
        pass

    async def after_exit(self):
        pass
