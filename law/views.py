from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Count
from django.shortcuts import render, get_object_or_404
from django.utils.translation import ugettext as _

from . import models


def build_laws_list_context(context, GET):
    key = _('search')
    if key in GET and GET[key]:
        context[key] = GET[key]
        context['laws'] = context['laws'].filter(text__search=GET[key])
        context['search'] = GET[key]

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
    context = {'laws': models.Document.objects
        .exclude(type_id__in=[95, 97, 145, 150])
        .order_by("-dre_doc_id")
        .prefetch_related("type")}

    context = build_laws_list_context(context, request.GET)

    return render(request, "law/law_list/main.html", context)


def types_list(request):
    types = models.Type.objects.exclude(id__in=[95, 97, 145, 150]).annotate(count=Count('document')).order_by('name')

    context = {'types': types}

    return render(request, "law/type_list/main.html", context)


def type_view(request, type_id):
    type = get_object_or_404(models.Type, id=type_id)

    context = {'type': type,
               'laws': type.document_set.order_by("-date", "-number").prefetch_related("type")}

    context = build_laws_list_context(context, request.GET)

    return render(request, "law/type_view/main.html", context)


def law_view(request, law_id, slug=None):
    law = get_object_or_404(models.Document, id=law_id)

    context = {'law': law}

    return render(request, "law/document_view/main.html", context)


def analysis(request):
    return render(request, "law/analysis.html")


def law_analysis_eu_impact(request):
    return render(request, "law/analysis/eu_impact.html")


def law_analysis_time_series(request):
    return render(request, "law/analysis/laws_time_series.html")
