from website.models import PageContent, Organization

def site(request):
    context = {
        #"LAST_UPDATE": PageContent.objects.all().order_by("-last_update")[0],
        "URL": request.scheme + "://" + request.get_host(),
        "PARTNERS": Organization.objects.filter(is_partner=True).order_by("name"),
    }
    
    return context
