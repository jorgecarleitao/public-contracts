from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
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


def law_list(request):

    context = {'laws': models.LawDecree.objects.all().order_by("-date", "-number")}

    context = build_laws_list_context(context, request.GET)

    return render(request, "law/law_list/main.html", context)
