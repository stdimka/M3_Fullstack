from django.shortcuts import render
from django.http import HttpResponse, JsonResponse


def index(request):
    return HttpResponse('Home page!!!')


def blog_index(request):
    return HttpResponse('Blog page!!!', status=200)


def about(request):
    return render(request, 'about.html', context={})


def article(request, id):
    dictionary = request.GET
    # dictionary['id'] = id
    return JsonResponse(dictionary)
