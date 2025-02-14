import logging
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class CsrfLoggingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        logger.info("CSRF token from request: %s", request.META.get('CSRF_COOKIE'))
        logger.info("CSRF token from POST: %s", request.POST.get('csrfmiddlewaretoken'))
        return None
