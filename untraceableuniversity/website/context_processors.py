from website.models import PageContent

def site(request):
    
    context = {
        "LAST_UPDATE": PageContent.objects.all().order_by("-last_update")[0],
    }
    
    return context
