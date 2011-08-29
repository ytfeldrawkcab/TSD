from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login

from tsd.models import *
from tsd.forms import *

#public functions
            
def findparentinstance(parentforms, lookupprefix):
    for parentform in parentforms:
        if parentform.prefix == lookupprefix:
            return parentform.instance
    return None
            
def findparentprefix(parentforms, lookupinstance):
    for parentform in parentforms:
        if parentform.instance == lookupinstance:
            return parentform.prefix

#customer management
def editcustomer(request, customerid=None):
    if request.method == 'GET':
        if customerid:
            customer = Customer.objects.get(pk=customerid)
        else:
            customer = None
            
        contacts = CustomerContact.objects.filter(customer=customer)
        c = 0
        contactforms = []
        for contact in contacts:
            c += 1
            contactform = CustomerContactForm(instance=contact, prefix='c'+str(c))
            contactforms.append(contactform)
            
        addresses = CustomerAddress.objects.filter(customer=customer)
        a = 0
        addressforms = []
        for address in addresses:
            a += 1
            addressform = CustomerAddressForm(instance=address, prefix='a'+str(a))
            addressforms.append(addressform)
        
        if customer:
            maincontactprefix = findparentprefix(contactforms, customer.defaultmaincontact)
            shippingcontactprefix = findparentprefix(contactforms, customer.defaultshippingcontact)
            billingcontactprefix = findparentprefix(contactforms, customer.defaultbillingcontact)
            shippingaddressprefix = findparentprefix(addressforms, customer.defaultshippingaddress)
            billingaddressprefix = findparentprefix(addressforms, customer.defaultbillingaddress)
        else:
            maincontactprefix = None
            shippingcontactprefix = None
            billingcontactprefix = None
            shippingaddressprefix = None
            billingaddressprefix = None
        
        customerform = CustomerForm(instance=customer, initial={'contactcount':c, 'addresscount':a, 'maincontactprefix':maincontactprefix, 'shippingcontactprefix':shippingcontactprefix, 'billingcontactprefix':billingcontactprefix, 'shippingaddressprefix':shippingaddressprefix, 'billingaddressprefix':billingaddressprefix})
        
        return render_to_response('customers/edit.html', RequestContext(request, {'form':customerform, 'contactforms':contactforms, 'addressforms':addressforms}))
    else:
        passedvalidation = True
        contactcount = request.POST['contactcount']
        addresscount = request.POST['addresscount']
        contactforms = []
        addressforms = []
        
        customerform = CustomerForm(request.POST)
        if not customerform.is_valid():
            passedvalidation = False
            
        for c in xrange(1, int(contactcount)+1):
            contactform = CustomerContactForm(request.POST, prefix='c'+str(c))
            contactforms.append(contactform)
            if not contactform.is_valid():
                passedvalidation = False
                
        for a in xrange(1, int(addresscount)+1):
            addressform = CustomerAddressForm(request.POST, prefix='a'+str(a))
            addressforms.append(addressform)
            if not addressform.is_valid():
                passedvalidation = False
            
        if passedvalidation == False:
            return render_to_response('customers/edit.html', RequestContext(request, {'form':customerform, 'contactforms':contactforms, 'addressforms':addressforms}))
        
        else:
            customer = customerform.save(commit=False)
            customer.pk = customerform.cleaned_data['pk']
            customer.save()
            
            for contactform in contactforms:
                contact = contactform.save(commit=False)
                contact.pk = contactform.cleaned_data['pk']
                contact.customer = customer
                if contactform.cleaned_data['delete'] == 0:
                    contact.save()
                elif contact.pk:
                    contact.delete()
                
            for addressform in addressforms:
                address = addressform.save(commit=False)
                address.pk = addressform.cleaned_data['pk']
                address.customer = customer
                if addressform.cleaned_data['delete'] == 0:
                    address.save()
                elif address.pk:
                    address.delete()
                    
            customer.defaultmaincontact = findparentinstance(contactforms, customerform.cleaned_data['maincontactprefix'])
            customer.defaultshippingcontact = findparentinstance(contactforms, customerform.cleaned_data['shippingcontactprefix'])
            customer.defaultbillingcontact = findparentinstance(contactforms, customerform.cleaned_data['billingcontactprefix'])
            customer.defaultshippingaddress = findparentinstance(addressforms, customerform.cleaned_data['shippingaddressprefix'])
            customer.defaultbillingaddress = findparentinstance(addressforms, customerform.cleaned_data['billingaddressprefix'])
            customer.save()
                    
            print customerform.cleaned_data['maincontactprefix']
            
            return HttpResponseRedirect('/tsd/customers/' + str(customer.pk) + '/edit/')
            
def addcontact(request):
    prefix = request.GET['prefix']
    contactform = CustomerContactForm(prefix='c'+str(prefix))
    
    return render_to_response('customers/contact.html', {'contactform':contactform})

def addaddress(request):
    prefix = request.GET['prefix']
    addressform = CustomerAddressForm(prefix='a'+str(prefix))
    
    return render_to_response('customers/address.html', {'addressform':addressform})

#order management
@login_required
def editorder(request, orderid=None, customerid=None):
    if orderid:
        order = Order.objects.get(pk=orderid)
        customerid = order.customer.id
    else:
        order = None
        
    if request.method == "GET":
        customer = Customer.objects.get(pk=customerid)
        stylelist = Style.objects.all()
        servicelist = Service.objects.all()
        imprintlist = Imprint.objects.filter(Q(artwork__customer__pk=customerid) | Q(transcendent=True)).order_by('transcendent')
    
        #get a list of existing groups for this order
        groups = Group.objects.filter(order=order)
        
        #groups forms for this order
        styleforms = []
        sizeforms = []
        groupforms = []
        s = 1
        ss = 1
        g = 1
        
        existingorderstyles = OrderStyle.objects.filter(order=order).filter(group=None)
        for style in existingorderstyles:
            styleprefix = 's'+str(s)
            styleform = OrderStyleForm(instance=style, prefix=styleprefix, initial={'parentprefix':'', 'label':style.style})
            styleforms.append(styleform)
            s += 1
            
            sizes = StyleSize.objects.filter(style__orderstyle=style)
            for size in sizes:
                sizeprefix = 'ss'+str(ss)
                existingiize = OrderSize.objects.filter(orderstyle=style).filter(stylesize=size)
                if existingiize.count() == 1:
                    instance = existingiize[0]
                else:
                    instance = OrderSize(stylesize=size)
                sizeform = OrderSizeForm(instance=instance, prefix=sizeprefix, initial={'parentprefix':styleprefix, 'label':size.size.abbr})
                sizeforms.append(sizeform)
                ss += 1
        
        for group in groups:
            groupprefix = 'g'+str(g)
            groupform = GroupForm(instance=group, prefix=groupprefix)
            groupforms.append(groupform)
            g += 1
            
            existingstyles = OrderStyle.objects.filter(group=group)
            for style in existingstyles:
                styleprefix = 's'+str(s)
                styleform = OrderStyleForm(instance=style, prefix=styleprefix, initial={'parentprefix':groupprefix, 'label':style.style})
                styleforms.append(styleform)
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
                    sizeform = OrderSizeForm(instance=instance, prefix=sizeprefix, initial={'parentprefix':styleprefix, 'label':size.size.abbr})
                    sizeforms.append(sizeform)
                    ss += 1
        
        #get a list of existing imprints for this order
        imprints = OrderImprint.objects.filter(order=order)
        imprintforms = []
        groupimprintforms = [GroupImprintForm(prefix='%%%prefix%%%')]
        oi = 1
        gi = 1
        for imprint in imprints:
            imprintprefix = 'oi'+str(oi)
            
            imprintname = '' if not imprint.imprint else Imprint.objects.get(pk=imprint.imprint.pk).name
            setupname = '' if not imprint.setup else Setup.objects.get(pk=imprint.setup.pk).name
            
            imprintform = OrderImprintForm(instance=imprint, initial={'imprintname':imprintname, 'setupname':setupname}, prefix=imprintprefix)
            imprintform.fields['imprint'].queryset = Imprint.objects.filter(Q(customer=order.customer) | Q(transcendent=True))

            imprintforms.append(imprintform)
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
                groupimprintform = GroupImprintForm(instance=instance, prefix=groupimprintprefix, initial={'parentprefix':imprintprefix, 'groupprefix':groupprefix, 'exists':exists, 'groupname':group.name})
                groupimprintforms.append(groupimprintform)
                gi += 1
                
        services = OrderService.objects.filter(order=order)
        serviceforms = []
        groupserviceforms = [GroupServiceForm(prefix='%%%prefix%%%')]
        os = 1
        gs = 1
        for service in services:
            serviceprefix = 'os'+str(os)
            serviceform = OrderServiceForm(instance=service, initial={'label':service.service}, prefix=serviceprefix)
            serviceforms.append(serviceform)
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
                groupserviceform = GroupServiceForm(instance=instance, prefix=groupserviceprefix, initial={'parentprefix':serviceprefix, 'groupprefix':groupprefix, 'exists':exists, 'groupname':group.name})
                groupserviceforms.append(groupserviceform)
                gs += 1
        
        orderinitial = {'imprintcount':oi-1, 'groupimprintcount':gi-1, 'groupcount':g-1, 'stylecount':s-1, 'sizecount':ss-1, 'servicecount':os-1, 'groupservicecount':gs-1, 'customer':customerid}
        
        if not order:
            user = request.user
            maincontact = customer.defaultmaincontact
            shippingcontact = customer.defaultshippingcontact
            billingcontact = customer.defaultbillingcontact
            shippingaddress = customer.defaultshippingaddress
            billingaddress = customer.defaultbillingaddress
            orderinitial.update({'user':user, 'maincontact':maincontact, 'shippingcontact':shippingcontact, 'billingcontact':billingcontact, 'shippingaddress':shippingaddress, 'billingaddress':billingaddress})
            
        orderform = OrderForm(instance=order, initial=orderinitial)
        
        dyecolors = DyeColor.objects.all()
        
        return render_to_response('orders/edit.html', RequestContext(request, {'form':orderform, 'imprintforms':imprintforms, 'groupimprintforms':groupimprintforms, 'groupforms':groupforms, 'styleforms':styleforms, 'sizeforms':sizeforms, 'serviceforms':serviceforms, 'groupserviceforms':groupserviceforms, 'stylelist':stylelist, 'servicelist':servicelist, 'imprintlist':imprintlist, 'dyecolors':dyecolors}))
    else:
        passedvalidation = True
        imprintforms = []
        groupimprintforms = []
        groupforms = []
        styleforms = []
        sizeforms = []
        serviceforms = []
        groupserviceforms = []
    
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
            if not imprintform.is_valid():
                passedvalidation = False
        
        for g in xrange(1, groupcount+1):
            groupform = GroupForm(request.POST, prefix='g'+str(g))
            groupforms.append(groupform)
            if not groupform.is_valid():
                passedvalidation = False
                
        for gi in xrange(1, groupimprintcount+1):
            groupimprintform = GroupImprintForm(request.POST, prefix='gi'+str(gi))
            groupimprintforms.append(groupimprintform)
            if not groupimprintform.is_valid():
                passedvalidation = False
        
        for s in xrange(1, stylecount+1):
            styleform = OrderStyleForm(request.POST, prefix='s'+str(s))
            styleforms.append(styleform)
            if not styleform.is_valid():
                passedvalidation = False
        
        for ss in xrange(1, sizecount+1):
            sizeform = OrderSizeForm(request.POST, prefix='ss'+str(ss))
            sizeforms.append(sizeform)
            if not sizeform.is_valid():
                passedvalidation = False
                
        for os in xrange(1, servicecount+1):
            serviceform = OrderServiceForm(request.POST, prefix='os'+str(os))
            serviceforms.append(serviceform)
            if not serviceform.is_valid():
                passedvalidation = False
                
        for gs in xrange(1, groupservicecount+1):
            groupserviceform = GroupServiceForm(request.POST, prefix='gs'+str(gs))
            groupserviceforms.append(groupserviceform)
            if not groupserviceform.is_valid():
                passedvalidation = False
               
        if not passedvalidation:
            groupimprintforms.append(GroupImprintForm(prefix='%%%prefix%%%'))
            groupserviceforms.append(GroupServiceForm(prefix='%%%prefix%%%'))
            stylelist = Style.objects.all()
            servicelist = Service.objects.all()
            imprintlist = Imprint.objects.filter(Q(artwork__customer__pk=request.POST['customer']) | Q(transcendent=True)).order_by('transcendent')
            return render_to_response('orders/edit.html', RequestContext(request, {'form':orderform, 'imprintforms':imprintforms, 'groupimprintforms':groupimprintforms, 'groupforms':groupforms, 'styleforms':styleforms, 'sizeforms':sizeforms, 'serviceforms':serviceforms, 'groupserviceforms':groupserviceforms, 'stylelist':stylelist, 'servicelist':servicelist, 'imprintlist':imprintlist}))
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
    
def addgroup(request):
    prefix = request.GET['prefix']
    form = GroupForm(initial={'name':'[unnamed]'}, prefix='g'+str(prefix))
    return render_to_response('orders/group.html', {'groupforms':[form]})
    
def addstyle(request):
    groupprefix = request.GET['groupprefix']
    styleprefix = 's' + request.GET['styleprefix']
    sizecount = int(request.GET['sizeprefix'])

    style = Style.objects.get(pk=request.GET['styleid'])
    sizes = StyleSize.objects.filter(style=style)

    styleform = OrderStyleForm(instance=OrderStyle(style=style), initial={'parentprefix':groupprefix, 'label':style}, prefix=styleprefix)
    sizeforms = []
    for size in sizes:
        sizeform = OrderSizeForm(instance=OrderSize(stylesize=size), initial={'parentprefix':styleprefix, 'label':size.size.abbr}, prefix='ss'+str(sizecount))
        sizeforms.append(sizeform)
        sizecount += 1

    return render_to_response('orders/style.html', {'styleform':styleform, 'sizeforms':sizeforms, 'sizecount':sizes.count})

def addimprint(request):
    customer = Customer.objects.get(pk=request.GET['customerid'])
    prefix = 'oi' + str(request.GET['prefix'])
    imprintform = OrderImprintForm(prefix=prefix)
    imprintform.fields['imprint'].queryset = Imprint.objects.filter(Q(customer=customer) | Q(transcendent=True))
    imprintforms = [imprintform]
    
    return render_to_response('orders/imprint.html', {'imprintforms':imprintforms})

def addservice(request):
    prefix = 'os' + str(request.GET['prefix'])
    service = Service.objects.get(pk=request.GET['serviceid'])
    
    serviceform = OrderServiceForm(initial={'service':service, 'label':service}, prefix=prefix)
    if service.enteredquantity == True:
        serviceform.fields['specify'].widget.attrs['disabled'] = 'disabled'
    else:
        serviceform.fields['quantity'].widget.attrs['disabled'] = 'disabled'
    serviceforms = [serviceform]
    
    return render_to_response('orders/service.html', {'serviceforms':serviceforms})
    
def getstyleprices(request):
    style = Style.objects.get(pk=request.GET['styleid'])
    styleprices = StylePrice.objects.filter(style=style)
    dyecolors = DyeColor.objects.all()
    
    return render_to_response('orders/styleprices.html', {'styleprices':styleprices, 'dyecolors':dyecolors})
    
#style management
def editstyle(request, styleid=None):
    if request.method == 'GET':
        if styleid:
            style = Style.objects.get(pk=styleid)
        else:
            style = None
        
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
            sizeform = StyleSizeForm(instance=instance, initial={'exists':exists, 'label':size.abbr, 'size':size}, prefix='s'+str(s))
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
            addedcostform = StylePriceAddedCostForm(instance=addedcost, initial={'parentprefix':parentprefix, 'sizeprefix':findparentprefix(sizeforms, addedcost.stylesize)}, prefix='ac'+str(ac))
            existingsizes = StyleSize.objects.filter(style=style)
            for existingsize in existingsizes:
                addedcostform.fields['sizeprefix'].choices.append((findparentprefix(sizeforms, existingsize), existingsize.size.abbr))
            addedcostforms.append(addedcostform)
            
        if style:
            garmentdyepriceprefix = findparentprefix(priceforms, style.garmentdyeprice)
        else:
            garmentdyepriceprefix = None
        
        styleform = StyleForm(instance=style, initial={'garmentdyepriceprefix':garmentdyepriceprefix, 'sizecount':s, 'pricecount':p, 'addedcostcount':ac})
        
        return render_to_response('styles/edit.html', RequestContext(request, {'form':styleform, 'sizeforms':sizeforms, 'priceforms':priceforms, 'addedcostforms':addedcostforms}))
        
    else:
    
        passedvalidation = True
        sizeforms = []
        priceforms = []
        addedcostforms = []
        
        sizecount = request.POST['sizecount']
        pricecount = request.POST['pricecount']
        addedcostcount = request.POST['addedcostcount']
        
        styleform = StyleForm(request.POST)
        if not styleform.is_valid():
            passedvalidation = False
        
        for s in xrange(1, int(sizecount)+1):
            sizeform = StyleSizeForm(request.POST, prefix='s'+str(s))
            sizeforms.append(sizeform)
            if not sizeform.is_valid():
                passedvalidation = False
        
        for p in xrange(1, int(pricecount)+1):
            priceform = StylePriceForm(request.POST, prefix='p'+str(p))
            priceforms.append(priceform)
            if not priceform.is_valid():
                passedvalidation = False
                
        for ac in xrange(1, int(addedcostcount)+1):
            addedcostform = StylePriceAddedCostForm(request.POST, prefix='ac'+str(ac))
            for sizeform in sizeforms:
                addedcostform.fields['sizeprefix'].choices.append((sizeform.prefix,''))
            addedcostforms.append(addedcostform)
            if not addedcostform.is_valid():
                passedvalidation = False

        if not passedvalidation:
            return render_to_response('styles/edit.html', RequestContext(request, {'form':styleform, 'sizeforms':sizeforms, 'priceforms':priceforms, 'addedcostforms':addedcostforms}))
        
        else:
            style = styleform.save(commit=False)
            style.pk = styleform.cleaned_data['pk']
            style.save()
            
            for sizeform in sizeforms:
                size = sizeform.save(commit=False)
                size.pk = sizeform.cleaned_data['pk']
                size.style = style
                if sizeform.cleaned_data['exists']:
                    size.save()
                elif size.pk:
                    size.delete()
                    
            for priceform in priceforms:
                price = priceform.save(commit=False)
                price.pk = priceform.cleaned_data['pk']
                price.style = style
                if priceform.cleaned_data['delete'] == 0:
                    price.save()
                elif price.pk:
                    price.delete()
                    
            for addedcostform in addedcostforms:
                addedcost = addedcostform.save(commit=False)
                addedcost.pk = addedcostform.cleaned_data['pk']
                price = findparentinstance(priceforms, addedcostform.cleaned_data['parentprefix'])
                addedcost.styleprice = price
                size = findparentinstance(sizeforms, addedcostform.cleaned_data['sizeprefix'])
                addedcost.stylesize = size
                if addedcostform.cleaned_data['delete'] == 0 and price.id:
                    addedcost.save()
                elif addedcost.pk:
                    addedcost.delete()
                    
            style.garmentdyeprice = findparentinstance(priceforms, styleform.cleaned_data['garmentdyepriceprefix'])
            style.save()
            
            return HttpResponseRedirect('/tsd/styles/' + str(style.pk) + '/edit/')
            
def addprice(request):
    prefix = 'p' + str(request.GET['prefix'])
    priceform = StylePriceForm(prefix=prefix)
    return render_to_response('styles/price.html', {'priceform':priceform})
    
def addaddedcost(request):
    prefix = 'ac' + str(request.GET['prefix'])
    parentprefix = request.GET['parentprefix']
    addedcostform = StylePriceAddedCostForm(initial={'parentprefix':parentprefix}, prefix=prefix)
    return render_to_response('styles/addedcost.html', {'addedcostform':addedcostform})
    
#size management
def editsizes(request):
    if request.method == 'GET':
        sizes = Size.objects.all()
        sizeforms = []
        s = 0
        for size in sizes:
            s += 1
            sizeform = SizeForm(instance=size, prefix=s)
            sizeforms.append(sizeform)
        
        return render_to_response('sizes/edit.html', RequestContext(request, {'forms':sizeforms, 'sizecount':s}))
        
    else:
        sizecount = request.POST['sizecount']
        sizeforms = []
        passedvalidation = True
        
        for s in xrange(1, int(sizecount)+1):
            sizeform = SizeForm(request.POST, prefix=s)
            sizeforms.append(sizeform)
            if not sizeform.is_valid():
                passedvalidation = False
                
        if passedvalidation == False:
            return render_to_response('sizes/edit.html', RequestContext(request, {'forms':sizeforms, 'sizecount':s}))
            
        else:
            for sizeform in sizeforms:
                size = sizeform.save(commit=False)
                size.pk = sizeform.cleaned_data['pk']
                if sizeform.cleaned_data['delete'] == 0:
                    size.save()
                elif size.pk:
                    size.delete()
        
        return HttpResponseRedirect('/tsd/sizes/edit/')
        
def addsize(request):
    prefix = request.GET['prefix']
    sizeform = SizeForm(prefix=prefix)
    return render_to_response('sizes/size.html', {'form':sizeform})
    
#artwork management
def editartwork(request, artworkid=None):
    if request.method == 'GET':
        if artworkid:
            artwork = Artwork.objects.get(pk=artworkid)
        else:
            artwork = None
        
        imprintforms = []
        i = 0
        imprints = Imprint.objects.filter(artwork=artwork)
        for imprint in imprints:
            i += 1
            imprintform = ImprintForm(instance=imprint, prefix='i'+str(i))
            imprintforms.append(imprintform)
            
        setupforms = []
        s = 0
        setups = Setup.objects.filter(imprint__artwork=artwork)
        for setup in setups:
            s += 1
            parentprefix = findparentprefix(imprintforms, setup.imprint)
            setupform = SetupForm(instance=setup, initial={'parentprefix':parentprefix}, prefix='s'+str(s))
            setupforms.append(setupform)
            
        setupcolorforms = []
        sc = 0
        setupcolors = SetupColor.objects.filter(setup__imprint__artwork=artwork)
        for setupcolor in setupcolors:
            sc += 1
            parentprefix = findparentprefix(setupforms, setupcolor.setup)
            setupcolorform = SetupColorForm(instance=setupcolor, initial={'parentprefix':parentprefix}, prefix='sc'+str(sc))
            setupcolorforms.append(setupcolorform)
        
        artworkform = ArtworkForm(instance=artwork, initial={'imprintcount':i, 'setupcount':s, 'setupcolorcount':sc})
        pressheads = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        
        return render_to_response('artwork/edit.html', RequestContext(request, {'form':artworkform, 'imprintforms':imprintforms, 'setupforms':setupforms, 'setupcolorforms':setupcolorforms, 'pressheads':pressheads}))
    
    else:
        
        passedvalidation = True
        imprintcount = request.POST['imprintcount']
        setupcount = request.POST['setupcount']
        setupcolorcount = request.POST['setupcolorcount']
        imprintforms = []
        setupforms = []
        setupcolorforms = []
        
        artworkform = ArtworkForm(request.POST)
        if not artworkform.is_valid():
            passedvalidation = False
            
        for i in xrange(1, int(imprintcount)+1):
            imprintform = ImprintForm(request.POST, prefix='i'+str(i))
            imprintforms.append(imprintform)
            if not imprintform.is_valid():
                passedvalidation = False
        
        for s in xrange(1, int(setupcount)+1):
            setupform = SetupForm(request.POST, request.FILES, prefix='s'+str(s))
            setupforms.append(setupform)
            if not setupform.is_valid():
                passedvalidation = False
                
        for sc in xrange(1, int(setupcolorcount)+1):
            setupcolorform = SetupColorForm(request.POST, prefix='sc'+str(sc))
            setupcolorforms.append(setupcolorform)
            if not setupcolorform.is_valid():
                passedvalidation = False
                
        if passedvalidation == False:
            pressheads = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
            return render_to_response('artwork/edit.html', RequestContext(request, {'form':artworkform, 'imprintforms':imprintforms, 'setupforms':setupforms, 'setupcolorforms':setupcolorforms, 'pressheads':pressheads}))
            
        else:
            artwork = artworkform.save(commit=False)
            artwork.pk = artworkform.cleaned_data['pk']
            artwork.save()
            
            for imprintform in imprintforms:
                imprint = imprintform.save(commit=False)
                imprint.pk = imprintform.cleaned_data['pk']
                imprint.artwork = artwork
                if imprintform.cleaned_data['delete'] == 0:
                    imprint.save()
                elif imprint.pk:
                    imprint.delete()
                    
            for setupform in setupforms:
                setup = setupform.save(commit=False)
                setup.pk = setupform.cleaned_data['pk']
                imprint = findparentinstance(imprintforms, setupform.cleaned_data['parentprefix'])
                setup.imprint = imprint
                if setupform.cleaned_data['delete'] == 0 and imprint.id:
                    setup.save()
                elif setup.pk:
                    setup.delete()
                    
            for setupcolorform in setupcolorforms:
                setupcolor = setupcolorform.save(commit=False)
                setupcolor.pk = setupcolorform.cleaned_data['pk']
                setup = findparentinstance(setupforms, setupcolorform.cleaned_data['parentprefix'])
                setupcolor.setup = setup
                if setupcolorform.cleaned_data['delete'] == 0 and setup.id:
                    setupcolor.save()
                elif setupcolor.pk:
                    setupcolor.delete()
                    
            return HttpResponseRedirect('/tsd/artwork/' + str(artwork.id) + '/edit/')
            
def addimprint(request):
    prefix = request.GET['prefix']
    imprintform = ImprintForm(prefix=prefix)
    return render_to_response('artwork/imprint.html', {'imprintform':imprintform})
    
def addsetup(request):
    prefix = 's' + str(request.GET['prefix'])
    parentprefix = request.GET['parentprefix']
    setupform = SetupForm(initial={'parentprefix':parentprefix}, prefix=prefix)
    pressheads = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    return render_to_response('artwork/setup.html', {'setupform':setupform, 'pressheads':pressheads})
    
def addsetupcolor(request):
    prefix = 'sc' + str(request.GET['prefix'])
    parentprefix = request.GET['parentprefix']
    setupcolorform = SetupColorForm(initial={'parentprefix':parentprefix}, prefix=prefix)
    return render_to_response('artwork/setupcolor.html', {'setupcolorform':setupcolorform})

#needed for admin for some reason O.o
def addgroupimprint(request):
    pass
    
def addpricecolor(request):
    pass
