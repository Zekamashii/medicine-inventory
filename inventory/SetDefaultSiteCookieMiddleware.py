class SetDefaultSiteCookieMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        default_site_id = request.session.pop('default_site_id', None)
        if default_site_id:
            response.set_cookie('selectedSite', default_site_id)
        return response
