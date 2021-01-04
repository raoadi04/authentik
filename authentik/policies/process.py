"""authentik policy task"""
from multiprocessing import Process
from multiprocessing.connection import Connection
from traceback import format_tb
from typing import Optional

from django.core.cache import cache
from sentry_sdk.hub import Hub
from sentry_sdk.tracing import Span
from structlog.stdlib import get_logger

from authentik.events.models import Event, EventAction
from authentik.policies.exceptions import PolicyException
from authentik.policies.models import PolicyBinding
from authentik.policies.types import PolicyRequest, PolicyResult

LOGGER = get_logger()


def cache_key(binding: PolicyBinding, request: PolicyRequest) -> str:
    """Generate Cache key for policy"""
    prefix = f"policy_{binding.policy_binding_uuid.hex}_{binding.policy.pk.hex}"
    if request.http_request and hasattr(request.http_request, "session"):
        prefix += f"_{request.http_request.session.session_key}"
    if request.user:
        prefix += f"#{request.user.pk}"
    return prefix


class PolicyProcess(Process):
    """Evaluate a single policy within a seprate process"""

    connection: Connection
    binding: PolicyBinding
    request: PolicyRequest

    def __init__(
        self,
        binding: PolicyBinding,
        request: PolicyRequest,
        connection: Optional[Connection],
    ):
        super().__init__()
        self.binding = binding
        self.request = request
        if not isinstance(self.request, PolicyRequest):
            raise ValueError(f"{self.request} is not a Policy Request.")
        if connection:
            self.connection = connection

    def create_event(self, action: str, **kwargs):
        """Create event with common values from `self.request` and `self.binding`."""
        event = Event.new(
            action=action,
            policy_uuid=self.binding.policy.policy_uuid.hex,
            request={
                # We can't pass the request 1:1 because it may contain a HTTPRequest
                # with values that we can't pickle
                "context": self.request.context,
                "obj": self.request.obj,
            },
            **kwargs,
        )
        event.set_user(self.request.user)
        if self.request.http_request:
            event.from_http(self.request.http_request)
        else:
            event.save()

    def execute(self) -> PolicyResult:
        """Run actual policy, returns result"""
        LOGGER.debug(
            "P_ENG(proc): Running policy",
            policy=self.binding.policy,
            user=self.request.user,
            process="PolicyProcess",
        )
        try:
            policy_result = self.binding.policy.passes(self.request)
            if self.binding.policy.execution_logging:
                self.create_event(EventAction.POLICY_EXECUTION, result=policy_result)
        except PolicyException as exc:
            # Create policy exception event
            error_string = "\n".join(format_tb(exc.__traceback__) + [str(exc)])
            self.create_event(EventAction.POLICY_EXCEPTION, error=error_string)
            LOGGER.debug("P_ENG(proc): error", exc=exc)
            policy_result = PolicyResult(False, str(exc))
        policy_result.source_policy = self.binding.policy
        # Invert result if policy.negate is set
        if self.binding.negate:
            policy_result.passing = not policy_result.passing
        LOGGER.debug(
            "P_ENG(proc): Finished",
            policy=self.binding.policy,
            result=policy_result,
            process="PolicyProcess",
            passing=policy_result.passing,
            user=self.request.user,
        )
        key = cache_key(self.binding, self.request)
        cache.set(key, policy_result)
        LOGGER.debug("P_ENG(proc): Cached policy evaluation", key=key)
        return policy_result

    def run(self):  # pragma: no cover
        """Task wrapper to run policy checking"""
        with Hub.current.start_span(
            op="policy.process.execute",
        ) as span:
            span: Span
            span.set_data("policy", self.binding.policy)
            span.set_data("request", self.request)
            try:
                self.connection.send(self.execute())
            except Exception as exc:  # pylint: disable=broad-except
                LOGGER.warning(str(exc))
                self.connection.send(PolicyResult(False, str(exc)))
