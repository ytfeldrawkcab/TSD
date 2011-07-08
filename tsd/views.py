from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login

from tsd.models import Customer, Order, Group, OrderStyle, Style, StyleSize, OrderSize, Size, OrderImprint, Imprint, GroupSetup, Color
from tsd.forms import OrderForm, GroupForm, OrderStyleForm, OrderSizeForm, OrderImprintForm, GroupSetupForm

@login_required
def editorder(request, orderid=None, customerid=None):
    if orderid:
        order = Order.objects.get(pk=orderid)
        customerid = order.customer.id
    else:
        order = None
        
    if request.method == "GET":
        stylelist = Style.objects.all()
    
        #get a list of existing groups for this order
        groups = Group.objects.filter(order=order)
        
        #groups forms for this order
        styledics = []
        sizedics = []
        groupdics = []
        s = 1
        ss = 1
        g = 1
        groupoptions = []
        groupforms = []
        for group in groups:
            groupprefix = 'g'+str(g)
            groupform = GroupForm(instance=group, prefix=groupprefix)
            groupoptions.append((groupprefix, group.name))
            groupforms.append(groupform)
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
        
        #get a list of existing imprints for this order
        imprints = OrderImprint.objects.filter(order=order)
        imprintdics = []
        setupdics = []
        oi = 1
        gs = 1
        for imprint in imprints:
            imprintprefix = 'oi'+str(oi)
            imprintform = OrderImprintForm(instance=imprint, prefix=imprintprefix)
            imprintform.fields['imprint'].queryset = Imprint.objects.filter(Q(customer=order.customer) | Q(transcendent=True))
            imprintdics.append({'form':imprintform})
            oi += 1
            existingsetups = GroupSetup.objects.filter(orderimprint=imprint)
            for setup in existingsetups:
                setupprefix = 'gs'+str(gs)
                groupprefix = findparentprefix(groupforms, setup.group)
                setupform = GroupSetupForm(instance=setup, prefix=setupprefix, initial={'parentprefix':imprintprefix, 'groupprefix':groupprefix})
                setupform.fields['groupprefix'].choices += groupoptions
                setupdics.append({'form':setupform, 'parentprefix':imprintprefix})
                gs += 1
                
        orderform = OrderForm(instance=order, initial={'imprintcount':oi-1, 'setupcount':gs-1, 'groupcount':g-1, 'stylecount':s-1, 'sizecount':ss-1, 'customer':customerid})
        return render_to_response('orders/edit.html', RequestContext(request, {'form':orderform, 'imprintdics':imprintdics, 'setupdics':setupdics, 'groupdics':groupdics, 'styledics':styledics, 'sizedics':sizedics, 'stylelist':stylelist}))
    else:
        passedvalidation = True
        imprintforms = []
        imprintdics = []
        setupforms = []
        setupdics = []
        groupforms = []
        groupdics = []
        styleforms = []
        styledics = []
        sizeforms = []
        sizedics = []
        
        groupoptions = []
    
        imprintcount = int(request.POST['imprintcount'])
        setupcount = int(request.POST['setupcount'])
        groupcount = int(request.POST['groupcount'])
        stylecount = int(request.POST['stylecount'])
        sizecount = int(request.POST['sizecount'])
        
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
            groupoptions.append((groupform.prefix, request.POST['g'+str(g)+'-name']))
            groupdics.append({'form':groupform})
            if not groupform.is_valid():
                passedvalidation = False
                
        for gs in xrange(1, setupcount+1):
            setupform = GroupSetupForm(request.POST, prefix='gs'+str(gs))
            setupform.fields['groupprefix'].choices += groupoptions
            setupforms.append(setupform)
            setupdics.append({'form':setupform, 'parentprefix':request.POST['gs'+str(gs)+'-parentprefix']})
            if not setupform.is_valid():
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
            stylelist = Style.objects.all()
            return render_to_response('orders/edit.html', RequestContext(request, {'form':orderform, 'imprintdics':imprintdics, 'setupdics':setupdics, 'groupdics':groupdics, 'styledics':styledics, 'sizedics':sizedics, 'stylelist':stylelist}))
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
                style.group = findparentinstance(groupforms, styleform.cleaned_data['parentprefix'])
                styledelete = styleform.cleaned_data['delete']
                if styledelete == 0 and style.group.id:
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
            
            for setupform in setupforms:
                setup = setupform.save(commit=False)
                setup.pk = setupform.cleaned_data['pk']
                setup.orderimprint = findparentinstance(imprintforms, setupform.cleaned_data['parentprefix'])
                setup.group = findparentinstance(groupforms, setupform.cleaned_data['groupprefix'])
                setupdelete = setupform.cleaned_data['delete']
                if setupdelete == 0 and setup.orderimprint.id and setup.group.id:
                    setup.save()
                elif setup.pk:
                    setup.delete()
            
            return HttpResponseRedirect('/tsd/orders/' + str(order.pk) + '/edit/')
            
def findparentinstance(parentforms, lookupprefix):
    for parentform in parentforms:
        if parentform.prefix == lookupprefix:
            return parentform.instance
            
def findparentprefix(parentforms, lookupinstance):
    for parentform in parentforms:
        if parentform.instance == lookupinstance:
            return parentform.prefix
    
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
    styleform.fields['color'].queryset = Color.objects.filter(Q(garmentdye=True) | Q(stylecolorprice__styleprice__style=style))
    styledics = [{'form':styleform, 'label':style, 'parentprefix':groupprefix, 'sizecount':sizes.count()}]
    sizedics = []
    for size in sizes:
        sizeform = OrderSizeForm(instance=OrderSize(stylesize=size), initial={'parentprefix':styleprefix}, prefix='ss'+str(sizecount))
        sizedics.append({'form':sizeform, 'label':size.size.abbr, 'parentprefix':styleprefix})
        sizecount += 1

    return render_to_response('orders/style.html', {'styledics':styledics, 'sizedics':sizedics})

def addimprint(request):
    customer = Customer.objects.get(pk=request.GET['customerid'])
    prefix = 'oi' + str(request.GET['prefix'])
    imprintform = OrderImprintForm(prefix=prefix)
    imprintform.fields['imprint'].queryset = Imprint.objects.filter(Q(customer=customer) | Q(transcendent=True))
    imprintdics = [{'form':imprintform}]
    
    return render_to_response('orders/imprint.html', {'imprintdics':imprintdics})
    
def addsetup(request):
    parentprefix = request.GET['parentprefix']
    prefix = 'gs' + str(request.GET['prefix'])
    setupform = GroupSetupForm(initial={'parentprefix':parentprefix}, prefix=prefix)
    setupdics = [{'form':setupform}]
    
    return render_to_response('orders/setup.html', {'setupdics':setupdics})

