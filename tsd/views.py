from django.shortcuts import render_to_response

from tsd.forms import OrderForm

def addorder(request):
    orderform = OrderForm()
    return render_to_response('orders/add.html', {"orderform":orderform})
