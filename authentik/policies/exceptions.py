"""policy exceptions"""

from authentik.lib.sentry import SentryIgnoredException


class PolicyEngineException(SentryIgnoredException):
    """Error raised when a policy engine is configured incorrectly"""


class PolicyException(SentryIgnoredException):
    """Exception that should be raised during Policy Evaluation, and can be recovered from."""

    src_exc: Exception | None = None

    def __init__(self, src_exc: Exception | None = None) -> None:
        super().__init__()
        self.src_exc = src_exc
