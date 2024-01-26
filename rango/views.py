from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    # return HttpResponse("Rango says hey there partner! <a href='/rango/about/'>About</a>")
    # Construct a dictionary to pass to the template as its context.
    context_dict = {'boldmessage': 'Crunchy, creamy, cookie, candy, cupcake!'}

    # Return a rendered response to send to the client.
    # We make use of the shortcut function, the first paramter is the template we wish to use
    return render(request, 'rango/index.html', context=context_dict)

def about(request):
    # return HttpResponse("Rango says here is the about page. <a href='/rango/'>Index</a>")

    context_dict = {'boldmessage': "This tutorial has been put together by " , 'emphasismessage': "Saranya Arul"}

    return render(request, 'rango/about.html', context=context_dict)