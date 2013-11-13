from django.shortcuts import render


def robots(request):
    return render(request, 'robots.txt', content_type='text/plain')
