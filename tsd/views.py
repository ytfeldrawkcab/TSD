from django.shortcuts import render_to_response

from tsd.models import Customer, Order, Group
from tsd.forms import OrderForm, GroupForm, OrderStyleForm

def editorder(request, orderid):
    #order = Order(customer=Customer.objects.get(pk=1))
    #order.save()
    
    order = Order.objects.get(pk=orderid)
    
    orderform = OrderForm(instance=order)
    
    groups = Group.objects.filter(order=order)
    i = 1
    groupforms = []
    for group in groups:
        groupforms.append(GroupForm(instance=group, prefix=i))
        i += 1

    return render_to_response('orders/edit.html', {'orderform':orderform, 'groupforms':groupforms})
    
def addgroup(request):
    if 'orderid' in request.GET:
        order = Order.objects.get(pk=request.GET['orderid'])
    else:
        order = None
    groupform = GroupForm(instance=Group(order=order))
    return render_to_response('orders/group.html', {'groupforms':[groupform]})
    
def addstyle(request):
    styleform = OrderStyleForm()
    return render_to_response('orders/style.html', {'styleforms':[styleform]})
