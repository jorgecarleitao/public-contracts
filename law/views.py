from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Count
from django.shortcuts import render
from django.utils.translation import ugettext as _

import models


def build_laws_list_context(context, GET):
    paginator = Paginator(context['laws'], 20)
    page = GET.get(_('page'))
    try:
        context['laws'] = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        context['laws'] = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        context['laws'] = paginator.page(paginator.num_pages)

    return context


def home(request):
    return render(request, "law/home.html")


def law_list(request):

    context = {'laws': models.Document.objects.all().order_by("-date", "-number")}

    context = build_laws_list_context(context, request.GET)

    return render(request, "law/law_list/main.html", context)


def types_list(request):
    types = models.Type.objects.all().annotate(count=Count('document__id')).filter(count__gt=0).order_by('-count')

    context = {'types': types}

    return render(request, "law/type_list/main.html", context)
