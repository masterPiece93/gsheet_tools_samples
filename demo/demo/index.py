from django.shortcuts import render
def index_view(request):
    """[Index Page]"""
    __title__ = "Index"
    # index.html is loaded from sheets/templates
    return render(request, 'index.html', {"page_name": __title__})
