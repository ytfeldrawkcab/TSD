from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.db import transaction

from tsd.models import Customer, Order, Group, OrderStyle, Style, StyleSize, OrderSize, Size
from tsd.forms import OrderForm, GroupForm, OrderStyleForm, OrderSizeForm

#@transaction.commit_manually
def editorder(request, orderid):
    order = Order.objects.get(pk=orderid)
    if request.method == "GET":
        #get a list of existing groups for this order
        groups = Group.objects.filter(order=order)
        
        #groups forms for this order
        styledics = []
        sizedics = []
        groupdics = []
        s = 1
        ss = 1
        g = 1
        for group in groups:
            groupprefix = 'g'+str(g)
            groupform = GroupForm(instance=group, prefix=groupprefix)
            groupdics.append({'form':groupform})
            g += 1
            
            existingstyles = OrderStyle.objects.filter(group=group)
            for style in existingstyles:
                styleprefix = 's'+str(s)
                styleform = OrderStyleForm(instance=style, prefix=styleprefix, initial={'parentprefix':groupprefix})
                styledics.append({'form':styleform, 'label':style.style, 'parentprefix':groupprefix})
                s += 1
           
                #size forms & labels for this order
                sizes = StyleSize.objects.filter(style__orderstyle=style)
                for size in sizes:
                    sizeprefix = 'ss'+str(ss)
                    existingsize = OrderSize.objects.filter(orderstyle=style).filter(stylesize=size)
                    if existingsize.count() == 1:
                        instance = existingsize[0]
                    else:
                        instance = OrderSize(stylesize=size)
                    sizeform = OrderSizeForm(instance=instance, prefix=sizeprefix, initial={'parentprefix':styleprefix})
                    sizedics.append({'form':sizeform, 'label':size.size.abbr, 'parentprefix':styleprefix})
                    ss += 1
        #transaction.commit()
        orderform = OrderForm(instance=order, initial={'groupcount':g-1, 'stylecount':s-1, 'sizecount':ss-1})
        return render_to_response('orders/edit.html', RequestContext(request, {'form':orderform, 'groupdics':groupdics, 'styledics':styledics, 'sizedics':sizedics}))
    else:
        passedvalidation = True
        groupforms = []
        groupdics = []
        styleforms = []
        styledics = []
        sizeforms = []
        sizedics = []
    
        groupcount = int(request.POST['groupcount'])
        stylecount = int(request.POST['stylecount'])
        sizecount = int(request.POST['sizecount'])
        
        orderform = OrderForm(request.POST)
        if not orderform.is_valid():
            passedvalidation = False
        
        for g in xrange(1, groupcount+1):
            groupform = GroupForm(request.POST, prefix='g'+str(g))
            groupforms.append(groupform)
            groupdics.append({'form':groupform})
            if not groupform.is_valid():
                passedvalidation = False
        
        for s in xrange(1, stylecount+1):
            styleform = OrderStyleForm(request.POST, prefix='s'+str(s))
            styleforms.append(styleform)
            style = Style.objects.get(pk=request.POST['s'+str(s)+'-style'])
            styledics.append({'form':styleform, 'label':style, 'parentprefix':request.POST['s'+str(s)+'-parentprefix']})
            if not styleform.is_valid():
                passedvalidation = False
        
        for ss in xrange(1, sizecount+1):
            sizeform = OrderSizeForm(request.POST, prefix='ss'+str(ss))
            sizeforms.append(sizeform)
            size = Size.objects.get(stylesize__pk=request.POST['ss'+str(ss)+'-stylesize'])
            sizedics.append({'form':sizeform, 'label':size.abbr, 'parentprefix':request.POST['ss'+str(ss)+'-parentprefix']})
            if not sizeform.is_valid():
                passedvalidation = False
               
        if not passedvalidation:
            return render_to_response('orders/edit.html', RequestContext(request, {'form':orderform, 'groupdics':groupdics, 'styledics':styledics, 'sizedics':sizedics}))
        else:
            order = orderform.save(commit=False)
            order.pk = orderform.cleaned_data['pk']
            order.save()
            for groupform in groupforms:
                group = groupform.save(commit=False)
                group.pk = groupform.cleaned_data['pk']
                group.order = order
                groupdelete = groupform.cleaned_data['delete']
                if groupdelete == 0:
                    group.save()
                else:
                    group.delete()
                for styleform in styleforms:
                    if styleform.cleaned_data['parentprefix'] == groupform.prefix:
                        style = styleform.save(commit=False)
                        style.pk = styleform.cleaned_data['pk']
                        style.group = group
                        styledelete = styleform.cleaned_data['delete']
                        if styledelete == 0 and groupdelete == 0:
                            style.save()
                        else:
                            style.delete()
                            
                        for sizeform in sizeforms:
                            if sizeform.cleaned_data['parentprefix'] == styleform.prefix:
                                if sizeform.cleaned_data['quantity'] and styledelete == 0 and groupdelete == 0:
                                    size = sizeform.save(commit=False)
                                    size.pk = sizeform.cleaned_data['pk']
                                    size.orderstyle = style
                                    size.save()
                                else:
                                    size = OrderSize.objects.filter(pk=sizeform.cleaned_data['pk']).delete()
            
            return HttpResponseRedirect('/tsd/orders/' + str(order.pk) + '/edit/')
    
def addgroup(request):
    prefix = request.GET['prefix']
    form = GroupForm(prefix='g'+str(prefix))
    return render_to_response('orders/group.html', {'groupdics':[{'form':form}]})
    
def addstyle(request):
    groupprefix = request.GET['groupprefix']
    styleprefix = 's' + request.GET['styleprefix']
    sizecount = int(request.GET['sizeprefix'])

    style = Style.objects.get(pk=request.GET['styleid'])
    sizes = StyleSize.objects.filter(style=style)

    styleform = OrderStyleForm(instance=OrderStyle(style=style), initial={'parentprefix':groupprefix}, prefix=styleprefix)
    styledics = [{'form':styleform, 'label':style.number, 'parentprefix':groupprefix, 'sizecount':sizes.count()}]
    sizedics = []
    for size in sizes:
        sizeform = OrderSizeForm(instance=OrderSize(stylesize=size), initial={'parentprefix':styleprefix}, prefix='ss'+str(sizecount))
        sizedics.append({'form':sizeform, 'label':size.size.abbr, 'parentprefix':styleprefix})
        sizecount += 1

    return render_to_response('orders/style.html', {'styledics':styledics, 'sizedics':sizedics})
