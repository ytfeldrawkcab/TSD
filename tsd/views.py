from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.db import transaction

from tsd.models import Customer, Order, Group, OrderStyle, Style, StyleSize, OrderSize
from tsd.forms import OrderForm, GroupForm, OrderStyleForm, OrderSizeForm

#@transaction.commit_manually
def editorder(request, orderid):
    order = Order.objects.get(pk=orderid)
    if request.method == "GET":
        existinggroups = Group.objects.filter(order=order)
        orderform = OrderForm(instance=order, initial={'groupcount':existinggroups.count})

        g = 1
        groups = []
        for group in existinggroups:
            existingstyles = OrderStyle.objects.filter(group=group)
            form = GroupForm(instance=group, prefix='g'+str(g), initial={'stylecount':existingstyles.count})
            styles = []
            s=1
            for style in existingstyles:
                print style
                form = OrderStyleForm(instance=style, prefix='g'+str(g)+'-'+str(s))
                sizes = StyleSize.objects.filter(style=style.style)
                ss = 1
                sizeforms = []
                for size in sizes:
                    sizeform = OrderSizeForm(instance=OrderSize(stylesize=size), prefix=str(g)+'-'+str(s)+'-'+str(ss))
                    sizelabel = size.size.abbr
                    sizeforms.append({'form':sizeform, 'sizelabel':sizelabel})
                    ss += 1
                styles.append({'form':form, 'stylelabel':style.style.number, 'sizeforms':sizeforms})
                s+=1
                
            groups.append({'form':form,'orderstyles':styles})
            g += 1
        #transaction.commit()
        return render_to_response('orders/edit.html', RequestContext(request, {'orderform':orderform, 'groups':groups}))
    else:
        passedvalidation = True
        postdata = request.POST.copy()
        orderform = OrderForm(postdata, instance=order)
        if not orderform.is_valid():
            passedvalidation = False
        else:
            savedorder = orderform.save()
            groupcount = orderform.cleaned_data['groupcount']
            groupforms = []
            for g in xrange(1, groupcount+1):
                postdata['g'+str(g)+'-order'] = savedorder.pk
                group = GroupForm(postdata, prefix='g'+str(g))
                if not group.is_valid():
                    passedvalidation = False
                else:
                    savedgroup = group.save()
                stylecount = postdata['g'+str(g)+'-stylecount']
                styles = []
                for s in xrange(1, stylecount+1):
                    postdata['g'+str(g)+'-'+str(s)+'-group'] = savedgroup.pk
                    style = OrderStyleForm(postdata, prefix='g'+str(g)+'-'+str(s))
                    if not style.is_valid():
                        passedvalidation = False
                    else:
                        savedstyle = style.save()
                    sizecount = style.cleaned_data['sizecount']
                    sizes = []
                    for ss in xrange(1, sizecount+1):
                        postdata['g'+str(g)+'-'+str(s)+'-'+str(ss)+'-orderstyle'] = savedstyle.pk
                        size = OrderSizeForm(postdata, prefix='g'+str(g)+'-'+str(s)+'-'+str(ss))
                        if size.cleaned_data('quantity'):
                            if not size.is_valid():
                                passedvalidation = False
                                size.save()
                            sizes.append({'form':size, 'sizelabel':None})
                    styles.append({'form':style, 'stylelabel':None, 'sizeforms':sizes})
                groupsforms.append({'form':group, 'orderstyles':styles})
                            
            if passedvalidation:
                #transaction.commit()
                return HttpResponseRedirect('/tsd/orders/' + str(order.pk) + '/edit/')
            else:
                #transaction.rollback()
                return render_to_response('orders/edit.html', RequestContext(request, {'orderform':orderform, 'groups':groupforms}))
    
def addgroup(request):
    if 'orderid' in request.GET:
        order = Order.objects.get(pk=request.GET['orderid'])
    else:
        order = None
    prefix = request.GET['prefix']
    form = GroupForm(instance=Group(order=order), prefix='g'+str(prefix))
    return render_to_response('orders/group.html', {'groups':[{'form':form}]})
    
def addstyle(request):
    style = Style.objects.get(pk=request.GET['styleid'])
    groupprefix = request.GET['groupprefix']
    styleprefix = request.GET['styleprefix']
    sizes = StyleSize.objects.filter(style=style)
    styleform = OrderStyleForm(instance=OrderStyle(style=style), initial={'sizecount':sizes.count}, prefix=str(groupprefix)+'-'+str(styleprefix))
    sizeforms = []
    i = 1
    for size in sizes:
        sizeform = OrderSizeForm(instance=OrderSize(stylesize=size), prefix=str(groupprefix)+'-'+str(styleprefix)+'-'+str(i))
        sizelabel = size.size.abbr
        sizeforms.append({'form':sizeform, 'sizelabel':sizelabel})
        i += 1
    orderstyle = {'form':styleform, 'stylelabel':style.number, 'sizeforms':sizeforms}
    return render_to_response('orders/style.html', {'groups':[{'orderstyles':[orderstyle]}]})
