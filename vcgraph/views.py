from django.shortcuts import render
from django.http import HttpResponseBadRequest
from src import tools
from src.veracross import *
from .models import Error
from .imagegetter import choose_image
import traceback


def login(request):
    quarters = tools.get_possible_quarters()
    image = choose_image()
    return render(request, 'login.html', {'quarters': quarters, 'image': image})


def veracross(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        quarter = int(request.POST['quarter'])
        try:
            vc = Veracross(username, password, quarter)
        except BadUsername:
            return render(request, 'error.html', {'error': "you have typed an invalid username"})
        except LoginError:
            return render(request, 'error.html', {'error': "invalid username or password"})
        except Exception as e:
            traceback_string = "\n".join(traceback.format_exception(type(e), e, e.__traceback__))
            print(traceback_string)
            if not Error.objects.filter(traceback=traceback_string).exists():
                Error.objects.create(username=username, traceback=traceback_string)
            return render(request, 'error.html', {'error': "unknown"})
        # print(vc)
        return render(request, 'veracross.html', {'veracross': vc, 'graph_data': json.dumps(vc.graph.data)})
    else:
        return HttpResponseBadRequest("Request Must Be POST")
