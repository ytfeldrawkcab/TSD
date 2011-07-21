from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login

from tsd.models import *
from tsd.forms import *

#order management
@login_required
def editorder(request, orderid=None, customerid=None):
    if orderid:
        order = Order.objects.get(pk=orderid)
        customerid = order.customer.id
    else:
        order = None
        
    if request.method == "GET":
        stylelist = Style.objects.all()
        servicelist = Service.objects.all()
        imprintlist = Imprint.objects.filter(Q(customer__pk=customerid) | Q(transcendent=True)).order_by('transcendent')
    
        #get a list of existing groups for this order
        groups = Group.objects.filter(order=order)
        
        #groups forms for this order
        styledics = []
        sizedics = []
        groupdics = []
        s = 1
        ss = 1
        g = 1
        groupforms = []
        
        existingorderstyles = OrderStyle.objects.filter(order=order).filter(group=None)
        for style in existingorderstyles:
            styleprefix = 's'+str(s)
            styleform = OrderStyleForm(instance=style, prefix=styleprefix, initial={'parentprefix':''})
            styledics.append({'form':styleform, 'label':style.style})
            s += 1
            
            sizes = StyleSize.objects.filter(style__orderstyle=style)
            for size in sizes:
                sizeprefix = 'ss'+str(ss)
                existingiize = OrderSize.objects.filter(orderstyle=style).filter(stylesize=size)
                if existingiize.count() == 1:
                    instance = existingiize[0]
                else:
                    instance = OrderSize(stylesize=size)
                sizeform = OrderSizeForm(instance=instance, prefix=sizeprefix, initial={'parentprefix':styleprefix})
                sizedics.append({'form':sizeform, 'label':size.size.abbr})
                ss += 1
        
        for group in groups:
            groupprefix = 'g'+str(g)
            groupform = GroupForm(instance=group, prefix=groupprefix)
            groupforms.append(groupform)
            groupdics.append({'form':groupform})
            g += 1
            
            existingityles = OrderStyle.objects.filter(group=group)
            for style in existingityles:
                styleprefix = 's'+str(s)
                styleform = OrderStyleForm(instance=style, prefix=styleprefix, initial={'parentprefix':groupprefix})
                styledics.append({'form':styleform, 'label':style.style})
                s += 1
           
                #size forms & labels for this order
                sizes = StyleSize.objects.filter(style__orderstyle=style)
                for size in sizes:
                    sizeprefix = 'ss'+str(ss)
                    existingiize = OrderSize.objects.filter(orderstyle=style).filter(stylesize=size)
                    if existingiize.count() == 1:
                        instance = existingiize[0]
                    else:
                        instance = OrderSize(stylesize=size)
                    sizeform = OrderSizeForm(instance=instance, prefix=sizeprefix, initial={'parentprefix':styleprefix})
                    sizedics.append({'form':sizeform, 'label':size.size.abbr})
                    ss += 1
        
        #get a list of existing imprints for this order
        imprints = OrderImprint.objects.filter(order=order)
        imprintdics = []
        groupimprintdics = [{'form':GroupImprintForm(prefix='%%%prefix%%%')}]
        oi = 1
        gi = 1
        for imprint in imprints:
            imprintprefix = 'oi'+str(oi)
            imprintform = OrderImprintForm(instance=imprint, prefix=imprintprefix)
            imprintform.fields['imprint'].queryset = Imprint.objects.filter(Q(customer=order.customer) | Q(transcendent=True))
            
            imprintname = '' if not imprint.imprint else Imprint.objects.get(pk=imprint.imprint.pk).name
            setupname = '' if not imprint.setup else Setup.objects.get(pk=imprint.setup.pk).name

            imprintdics.append({'form':imprintform, 'imprintname': imprintname, 'setupname': setupname})
            oi += 1
            for group in groups:
                groupimprintprefix = 'gi'+str(gi)
                groupprefix = findparentprefix(groupforms, group)
                existinggroupimprint = GroupImprint.objects.filter(group=group).filter(orderimprint=imprint)
                if existinggroupimprint.count() == 1:
                    instance = existinggroupimprint[0]
                    exists = True
                else:
                    instance = None
                    exists = False
                groupimprintform = GroupImprintForm(instance=instance, prefix=groupimprintprefix, initial={'parentprefix':imprintprefix, 'groupprefix':groupprefix, 'exists':exists})
                groupimprintdics.append({'form':groupimprintform, 'groupname':group.name})
                gi += 1
                
        services = OrderService.objects.filter(order=order)
        servicedics = []
        groupservicedics = [{'form':GroupServiceForm(prefix='%%%prefix%%%')}]
        os = 1
        gs = 1
        for service in services:
            serviceprefix = 'os'+str(os)
            serviceform = OrderServiceForm(instance=service, prefix=serviceprefix)
            servicedics.append({'form':serviceform, 'label':service.service})
            os += 1
            for group in groups:
                groupserviceprefix = 'gs'+str(gs)
                groupprefix = findparentprefix(groupforms, group)
                existinggroupservice = GroupService.objects.filter(group=group).filter(orderservice=service)
                if existinggroupservice.count() == 1:
                    instance = existinggroupservice[0]
                    exists = True
                else:
                    instance = None
                    exists = False
                groupserviceform = GroupServiceForm(instance=instance, prefix=groupserviceprefix, initial={'parentprefix':serviceprefix, 'groupprefix':groupprefix, 'exists':exists})
                groupservicedics.append({'form':groupserviceform, 'groupname':group.name})
                gs += 1
                
        orderform = OrderForm(instance=order, initial={'imprintcount':oi-1, 'groupimprintcount':gi-1, 'groupcount':g-1, 'stylecount':s-1, 'sizecount':ss-1, 'servicecount':os-1, 'groupservicecount':gs-1, 'customer':customerid})
        
        return render_to_response('orders/edit.html', RequestContext(request, {'form':orderform, 'imprintdics':imprintdics, 'groupimprintdics':groupimprintdics, 'groupdics':groupdics, 'styledics':styledics, 'sizedics':sizedics, 'servicedics':servicedics, 'groupservicedics':groupservicedics, 'stylelist':stylelist, 'servicelist':servicelist, 'imprintlist':imprintlist}))
    else:
        passedvalidation = True
        imprintforms = []
        imprintdics = []
        groupimprintforms = []
        groupimprintdics = [{'form':GroupImprintForm(prefix='%%%prefix%%%')}]
        groupforms = []
        groupdics = []
        styleforms = []
        styledics = []
        sizeforms = []
        sizedics = []
        serviceforms = []
        servicedics = []
        groupserviceforms = []
        groupservicedics = [{'form':GroupServiceForm(prefix='%%%prefix%%%')}]
    
        imprintcount = int(request.POST['imprintcount'])
        groupimprintcount = int(request.POST['groupimprintcount'])
        groupcount = int(request.POST['groupcount'])
        stylecount = int(request.POST['stylecount'])
        sizecount = int(request.POST['sizecount'])
        servicecount = int(request.POST['servicecount'])
        groupservicecount = int(request.POST['groupservicecount'])
        
        orderform = OrderForm(request.POST)
        if not orderform.is_valid():
            passedvalidation = False
            
        for oi in xrange(1, imprintcount+1):
            imprintform = OrderImprintForm(request.POST, prefix='oi'+str(oi))
            imprintform.fields['imprint'].queryset = Imprint.objects.filter(Q(customer__pk=request.POST['customer']) | Q(transcendent=True))
            imprintforms.append(imprintform)
            imprintdics.append({'form':imprintform})
            if not imprintform.is_valid():
                passedvalidation = False
        
        for g in xrange(1, groupcount+1):
            groupform = GroupForm(request.POST, prefix='g'+str(g))
            groupforms.append(groupform)
            groupdics.append({'form':groupform})
            if not groupform.is_valid():
                passedvalidation = False
                
        for gi in xrange(1, groupimprintcount+1):
            groupimprintform = GroupImprintForm(request.POST, prefix='gi'+str(gi))
            groupimprintforms.append(groupimprintform)
            groupimprintdics.append({'form':groupimprintform})
            if not groupimprintform.is_valid():
                passedvalidation = False
        
        for s in xrange(1, stylecount+1):
            styleform = OrderStyleForm(request.POST, prefix='s'+str(s))
            styleforms.append(styleform)
            style = Style.objects.get(pk=request.POST['s'+str(s)+'-style'])
            styledics.append({'form':styleform, 'label':style})
            if not styleform.is_valid():
                passedvalidation = False
        
        for ss in xrange(1, sizecount+1):
            sizeform = OrderSizeForm(request.POST, prefix='ss'+str(ss))
            sizeforms.append(sizeform)
            size = Size.objects.get(stylesize__pk=request.POST['ss'+str(ss)+'-stylesize'])
            sizedics.append({'form':sizeform, 'label':size.abbr})
            if not sizeform.is_valid():
                passedvalidation = False
                
        for os in xrange(1, servicecount+1):
            serviceform = OrderServiceForm(request.POST, prefix='os'+str(os))
            serviceforms.append(serviceform)
            service = Service.objects.get(pk=request.POST['os'+str(os)+'-service'])
            servicedics.append({'form':serviceform, 'label':service.name})
            if not serviceform.is_valid():
                passedvalidation = False
                
        for gs in xrange(1, groupservicecount+1):
            groupserviceform = GroupServiceForm(request.POST, prefix='gs'+str(gs))
            groupserviceforms.append(groupserviceform)
            groupservicedics.append({'form':groupserviceform})
            if not groupserviceform.is_valid():
                passedvalidation = False
               
        if not passedvalidation:
            stylelist = Style.objects.all()
            servicelist = Service.objects.all()
            imprintlist = Imprint.objects.filter(Q(customer__pk=request.POST['customer']) | Q(transcendent=True)).order_by('transcendent')
            return render_to_response('orders/edit.html', RequestContext(request, {'form':orderform, 'imprintdics':imprintdics, 'groupimprintdics':groupimprintdics, 'groupdics':groupdics, 'styledics':styledics, 'sizedics':sizedics, 'servicedics':servicedics, 'groupservicedics':groupservicedics, 'stylelist':stylelist, 'servicelist':servicelist, 'imprintlist':imprintlist}))
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
                elif group.pk:
                    group.delete()
                    
            for styleform in styleforms:
                style = styleform.save(commit=False)
                style.pk = styleform.cleaned_data['pk']
                style.order = order
                style.group = findparentinstance(groupforms, styleform.cleaned_data['parentprefix'])
                styledelete = styleform.cleaned_data['delete']
                if styledelete == 0:
                    style.save()
                elif style.pk:
                    style.delete()
                            
            for sizeform in sizeforms:
                size = sizeform.save(commit=False)
                size.pk = sizeform.cleaned_data['pk']
                size.orderstyle = findparentinstance(styleforms, sizeform.cleaned_data['parentprefix'])
                if sizeform.cleaned_data['quantity'] and size.orderstyle.id:
                    size.save()
                elif size.pk:
                    size.delete()
            
            for imprintform in imprintforms:
                imprint = imprintform.save(commit=False)
                imprint.pk = imprintform.cleaned_data['pk']
                imprint.order = order
                imprintdelete = imprintform.cleaned_data['delete']
                if imprintdelete == 0:
                    imprint.save()
                elif imprint.pk:
                    imprint.delete()
            
            for groupimprintform in groupimprintforms:
                groupimprint = groupimprintform.save(commit=False)
                groupimprint.pk = groupimprintform.cleaned_data['pk']
                groupimprint.orderimprint = findparentinstance(imprintforms, groupimprintform.cleaned_data['parentprefix'])
                groupimprint.group = findparentinstance(groupforms, groupimprintform.cleaned_data['groupprefix'])
                groupimprintexists = groupimprintform.cleaned_data['exists']
                if groupimprintexists == True and groupimprint.orderimprint.id and groupimprint.group.id:
                    groupimprint.save()
                elif groupimprint.pk:
                    groupimprint.delete()
                    
            for serviceform in serviceforms:
                service = serviceform.save(commit=False)
                service.pk = serviceform.cleaned_data['pk']
                service.order = order
                servicedelete = serviceform.cleaned_data['delete']
                if servicedelete == 0:
                    service.save()
                elif service.pk:
                    service.delete()
                    
            for groupserviceform in groupserviceforms:
                groupservice = groupserviceform.save(commit=False)
                groupservice.pk = groupserviceform.cleaned_data['pk']
                groupservice.orderservice = findparentinstance(serviceforms, groupserviceform.cleaned_data['parentprefix'])
                groupservice.group = findparentinstance(groupforms, groupserviceform.cleaned_data['groupprefix'])
                groupserviceexists = groupserviceform.cleaned_data['exists']
                if groupserviceexists == True and groupservice.orderservice.id and groupservice.group.id:
                    groupservice.save()
                elif groupservice.pk:
                    groupservice.delete()
            
            return HttpResponseRedirect('/tsd/orders/' + str(order.pk) + '/edit/')
            
def findparentinstance(parentforms, lookupprefix):
    for parentform in parentforms:
        if parentform.prefix == lookupprefix:
            return parentform.instance
    return None
            
def findparentprefix(parentforms, lookupinstance):
    for parentform in parentforms:
        if parentform.instance == lookupinstance:
            return parentform.prefix
    
def addgroup(request):
    prefix = request.GET['prefix']
    form = GroupForm(initial={'name':'[unnamed]'}, prefix='g'+str(prefix))
    return render_to_response('orders/group.html', {'groupdics':[{'form':form}]})
    
def addstyle(request):
    groupprefix = request.GET['groupprefix']
    styleprefix = 's' + request.GET['styleprefix']
    sizecount = int(request.GET['sizeprefix'])

    style = Style.objects.get(pk=request.GET['styleid'])
    sizes = StyleSize.objects.filter(style=style)

    styleform = OrderStyleForm(instance=OrderStyle(style=style), initial={'parentprefix':groupprefix}, prefix=styleprefix)
    styleform.fields['color'].queryset = Color.objects.filter(Q(garmentdye=True) | Q(stylecolorprice__styleprice__style=style))
    styledic = {'form':styleform, 'label':style, 'parentprefix':groupprefix, 'sizecount':sizes.count()}
    sizedics = []
    for size in sizes:
        sizeform = OrderSizeForm(instance=OrderSize(stylesize=size), initial={'parentprefix':styleprefix}, prefix='ss'+str(sizecount))
        sizedics.append({'form':sizeform, 'label':size.size.abbr, 'parentprefix':styleprefix})
        sizecount += 1

    return render_to_response('orders/style.html', {'styledic':styledic, 'sizedics':sizedics})

def addimprint(request):
    customer = Customer.objects.get(pk=request.GET['customerid'])
    prefix = 'oi' + str(request.GET['prefix'])
    imprintform = OrderImprintForm(prefix=prefix)
    imprintform.fields['imprint'].queryset = Imprint.objects.filter(Q(customer=customer) | Q(transcendent=True))
    imprintdics = [{'form':imprintform}]
    
    return render_to_response('orders/imprint.html', {'imprintdics':imprintdics})
    
def addgroupimprint(request):
    groupprefix = request.GET['groupprefix']
    prefix = 'giprefix'
    groupimprintform = GroupImprintForm(initial={'groupprefix':groupprefix}, prefix=prefix)
    groupimprintdics = [{'form':groupimprintform}]
    
    return render_to_response('orders/groupimprint.html', {'groupimprintdics':groupimprintdics})

def addservice(request):
    prefix = 'os' + str(request.GET['prefix'])
    service = Service.objects.get(pk=request.GET['serviceid'])
    
    serviceform = OrderServiceForm(initial={'service':service}, prefix=prefix)
    if service.enteredquantity == True:
        serviceform.fields['specify'].widget.attrs['disabled'] = 'disabled'
    else:
        serviceform.fields['quantity'].widget.attrs['disabled'] = 'disabled'
    servicedics = [{'form':serviceform, 'label':service}]
    
    return render_to_response('orders/service.html', {'servicedics':servicedics})
    
#style management
def editstyle(request, styleid=None):
    if request.method == 'GET':
        if styleid:
            style = Style.objects.get(pk=styleid)
        else:
            style = None
        
        styleform = StyleForm(instance=style)
        
        sizes = Size.objects.all()
        sizeforms = []
        s = 0
        for size in sizes:
            s += 1
            existingsize = StyleSize.objects.filter(style=style).filter(size=size)
            if existingsize.count() == 1:
                instance = existingsize[0]
                exists = True
            else:
                instance = None
                exists = False
            sizeform = StyleSizeForm(instance=instance, initial={'exists':exists, 'label':size.abbr}, prefix='s'+str(s))
            sizeforms.append(sizeform)
        
        prices = StylePrice.objects.filter(style=style)
        priceforms = []
        p = 0
        for price in prices:
            p += 1
            priceform = StylePriceForm(instance=price, prefix='p'+str(p))
            priceforms.append(priceform)
        
        addedcosts = StylePriceAddedCost.objects.filter(styleprice__style=style)
        addedcostforms = []
        ac = 0
        for addedcost in addedcosts:
            ac += 1
            parentprefix = findparentprefix(priceforms, addedcost.styleprice)
            addedcostform = StylePriceAddedCostForm(instance=addedcost, initial={'parentprefix':parentprefix}, prefix='ac'+str(ac))
            addedcostforms.append(addedcostform)
        
        return render_to_response('styles/edit.html', RequestContext(request, {'form':styleform, 'sizeforms':sizeforms, 'priceforms':priceforms, 'addedcostforms':addedcostforms}))
