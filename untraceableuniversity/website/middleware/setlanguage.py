from django.utils import translation

def locale_middleware(get_response):

    def middleware(request):
        if request.get_full_path()[:4] == "/es/":
            language_code = "es"
        else:
            language_code = "en"

        translation.activate(language_code)
        request.language = language_code
        return get_response(request)

    return middleware
