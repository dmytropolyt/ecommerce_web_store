from .models import Category


def menu_links(request):
    """Context processor fot menu links."""
    links = Category.objects.all()
    return dict(links=links)
