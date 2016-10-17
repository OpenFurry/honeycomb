from django.shortcuts import render


def front(request):
    return render(request, 'front.html', {})
