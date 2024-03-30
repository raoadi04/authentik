"""custom runserver command"""

from typing import TextIO

from daphne.management.commands.runserver import Command as RunServer
from daphne.server import Server
from structlog.stdlib import get_logger

from authentik.root.signals import post_startup, pre_startup, startup


class SignalServer(Server):
    """Server which signals back to authentik when it finished starting up"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        def ready_callable():
            pre_startup.send(sender=self)
            startup.send(sender=self)
            post_startup.send(sender=self)

        self.ready_callable = ready_callable


class Command(RunServer):
    """custom runserver command, which doesn't show the misleading django startup message"""

    server_cls = SignalServer

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stdout = TextIO()
        self.logger = get_logger()

    def on_bind(self, server_port):
        pass
