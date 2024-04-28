from django.db.models import Model
from django.http import HttpResponseNotFound
from google.auth.exceptions import GoogleAuthError, TransportError
from googleapiclient.discovery import build
from googleapiclient.errors import Error, HttpError
from googleapiclient.http import HttpRequest
from httplib2 import HttpLib2Error, HttpLib2ErrorWithResponse

from authentik.enterprise.providers.google_workspace.models import GoogleWorkspaceProvider
from authentik.lib.sync.outgoing import HTTP_CONFLICT
from authentik.lib.sync.outgoing.base import BaseOutgoingSyncClient
from authentik.lib.sync.outgoing.exceptions import (
    NotFoundSyncException,
    ObjectExistsException,
    StopSync,
    TransientSyncException,
)


class GoogleWorkspaceSyncClient[TModel: Model, TSchema: dict](
    BaseOutgoingSyncClient[TModel, TSchema, GoogleWorkspaceProvider]
):
    """Base client for syncing to google workspace"""

    def __init__(self, provider: GoogleWorkspaceProvider) -> None:
        super().__init__(provider)
        self.directory_service = build(
            "admin",
            "directory_v1",
            credentials=provider.google_credentials(),
            cache_discovery=False,
        )

    def _request(self, request: HttpRequest):
        try:
            response = request.execute()
        except GoogleAuthError as exc:
            if isinstance(exc, TransportError):
                raise TransientSyncException(f"Failed to send request: {str(exc)}") from exc
            raise StopSync(exc) from exc
        except HttpLib2Error as exc:
            if isinstance(exc, HttpLib2ErrorWithResponse):
                self._response_handle_status_code(exc.response.status, exc)
            raise TransientSyncException(f"Failed to send request: {str(exc)}") from exc
        except HttpError as exc:
            self._response_handle_status_code(exc.status_code, exc)
            raise TransientSyncException(f"Failed to send request: {str(exc)}") from exc
        except Error as exc:
            raise TransientSyncException(f"Failed to send request: {str(exc)}") from exc
        return response

    def _response_handle_status_code(self, status_code: int, root_exc: Exception):
        if status_code == HttpResponseNotFound.status_code:
            raise NotFoundSyncException("Object not found") from root_exc
        if status_code == HTTP_CONFLICT:
            raise ObjectExistsException("Object exists") from root_exc
