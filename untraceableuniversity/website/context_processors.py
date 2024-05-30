from website.models import PageContent

def site(request):
    context = {
        #"LAST_UPDATE": PageContent.objects.all().order_by("-last_update")[0],
        "URL": request.scheme + "://" + request.get_host(),
    }
    
    return context
