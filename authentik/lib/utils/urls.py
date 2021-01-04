"""URL-related utils"""
from urllib.parse import urlparse

from django.http import HttpResponse
from django.shortcuts import redirect, reverse
from django.urls import NoReverseMatch
from django.utils.http import urlencode
from structlog.stdlib import get_logger

LOGGER = get_logger()


def is_url_absolute(url):
    """Check if domain is absolute to prevent user from being redirect somewhere else"""
    return bool(urlparse(url).netloc)


def redirect_with_qs(view: str, get_query_set=None, **kwargs) -> HttpResponse:
    """Wrapper to redirect whilst keeping GET Parameters"""
    try:
        target = reverse(view, kwargs=kwargs)
    except NoReverseMatch:
        if not is_url_absolute(view):
            return redirect(view)
        LOGGER.debug("redirect target is not a valid view", view=view)
        raise
    else:
        if get_query_set:
            target += "?" + urlencode(get_query_set.items())
        return redirect(target)
