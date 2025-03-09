import pathlib
from django.shortcuts import render
from django.http import HttpResponse

from visits.models import PageVisit

this_dir = pathlib.Path(__file__).resolve().parent


def home_page_view(request, *args, **kwargs):
    qs = PageVisit.objects.all()
    page_qs = PageVisit.objects.filter(page=request.path)
    my_title = "Hooklify"
    my_context = {
        "page_title": my_title,
        "page_visit_count": page_qs.count(),
        "total_visits_count": qs.count()
    }

    html_ = "index.html"
    PageVisit.objects.create(page=request.path)
    return render(request, html_, my_context)