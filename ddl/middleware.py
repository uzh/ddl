from mozilla_django_oidc.middleware import SessionRefresh

OIDC_AUTH_REQUIRED_PATHS = ["/ddm/projects"]

class ConditionalSessionRefreshMiddleware(SessionRefresh):
    """Disables OIDC authentication check on certain paths."""

    def process_request(self, request):
        if request.path in OIDC_AUTH_REQUIRED_PATHS:
            return super().process_request(request)
        return None
