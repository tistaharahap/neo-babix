from neobabix.playbooks.playbook import Playbook


class HitAndRun(Playbook):
    __name__ = 'HitAndRun Playbook'

    """
        This is the simplest playbook.
        
        Entry:
            - Buy asset using market order
        Exit:
            - Immediately send an exit limit order at a predetermined percentage
            - Immediately send a stop limit order at a predetermined percentage
    """

    def entry(self):
        pass

    def after_entry(self):
        pass

    def exit(self):
        pass

    def after_exit(self):
        pass
