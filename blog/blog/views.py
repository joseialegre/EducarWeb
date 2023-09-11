from django.http import HttpResponseNotFound
from django.shortcuts import render


def pagina404(request,exception):
    pagina = "<head> <title> Pagina no encontrada </title> </head><div style='width: 100%;margin: auto;display: grid;justify-content: center;'><h1 style='font-size: 3rem;border-bottom: 1px solid green;'>Pagina no encontrada</h1> <p style='display:flex ; margin:auto'>ERROR 404</p></div> "
    return HttpResponseNotFound(pagina)
def about(request):
    return render(request,'about/about.html')