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
        #get a list of existing groups for this order
        existinggroups = Group.objects.filter(order=order)
        #instantiate the form for this order and put in a count of the groups in the order
        orderform = OrderForm(instance=order, initial={'groupcount':existinggroups.count})
        #initialize a variable for the group prefix and create a list for the groups
        g = 1
        groupdics = []
        for group in existinggroups:
            #get a list of style records for the iterated group
            existingstyles = OrderStyle.objects.filter(group=group)
            #instantiate a form for the group and include a count of styles (THIS IS NOT APPEARING ON THE PAGE FOR SOME REASON)
            groupform = GroupForm(instance=group, prefix='g'+str(g), initial={'stylecount':existingstyles.count})
            styledics = []
            s=1
            for style in existingstyles:
                #get a list of sizes available for this style
                sizes = StyleSize.objects.filter(style=style.style)
                #instantiate a form for this style
                styleform = OrderStyleForm(instance=style, prefix='g'+str(g)+'-'+str(s))
                ss = 1
                sizedics = []
                for size in sizes:
                    #generate a form for the iterated size
                    sizeform = OrderSizeForm(instance=OrderSize(stylesize=size), prefix=str(g)+'-'+str(s)+'-'+str(ss))
                    #get a label for the size abbreviation
                    sizelabel = size.size.abbr
                    #add a dictionary to the size list with the size form and size label
                    sizedics.append({'form':sizeform, 'label':sizelabel})
                    ss += 1
                #add a dictionary to the styles list with the form for each style, a label for each style, and the dictionary of size data
                styledics.append({'form':styleform, 'label':style.style.number, 'sizedics':sizedics})
                s+=1
                
            #add a dictionary of the group form plus the dictionary of style data (which includes a dictionary of size data)
            groupdics.append({'form':groupform,'styledics':styledics})
            g += 1
        #transaction.commit()
        return render_to_response('orders/edit.html', RequestContext(request, {'form':orderform, 'groupdics':groupdics}))
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
            #groups
            for g in xrange(1, groupcount+1):
                postdata['g'+str(g)+'-order'] = savedorder.pk
                group = GroupForm(postdata, prefix='g'+str(g))
                if not group.is_valid():
                    passedvalidation = False
                else:
                    savedgroup = group.save()
                stylecount = postdata['g'+str(g)+'-stylecount']
                styles = []
                #styles
                for s in xrange(1, stylecount+1):
                    postdata['g'+str(g)+'-'+str(s)+'-group'] = savedgroup.pk
                    style = OrderStyleForm(postdata, prefix='g'+str(g)+'-'+str(s))
                    if not style.is_valid():
                        passedvalidation = False
                    else:
                        savedstyle = style.save()
                    sizecount = style.cleaned_data['sizecount']
                    sizes = []
                    #sizes
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
    #get style to add to form
    style = Style.objects.get(pk=request.GET['styleid'])
    #get prefix of group style will be added to
    groupprefix = request.GET['groupprefix']
    #get unique prefix for actual style
    styleprefix = request.GET['styleprefix']
    #get a list of sizes valid for chosen style
    sizes = StyleSize.objects.filter(style=style)
    #generate form for style (including value for the count of sizes in style)
    styleform = OrderStyleForm(instance=OrderStyle(style=style), initial={'sizecount':sizes.count}, prefix=str(groupprefix)+'-'+str(styleprefix))
    sizedics = []
    i = 1
    #generate a size form for each size available for style
    for size in sizes:
        sizeform = OrderSizeForm(instance=OrderSize(stylesize=size), prefix=str(groupprefix)+'-'+str(styleprefix)+'-'+str(i))
        sizelabel = size.size.abbr
        #this is a dictionary with the form for the size, plus a label for the size abbreviation
        sizedics.append({'form':sizeform, 'label':sizelabel})
        i += 1
    #this is a dictionary that includes the form for the style, the label for the style, and the dictionary of size data
    styledic = {'form':styleform, 'label':style.number, 'sizedics':sizedics}
    #attempting to get this to work with the existing data generated by the full order form, I'd put the styles in an additional dictionary for the groups so that the template will render correctly
    return render_to_response('orders/style.html', {'groupdics':[{'styledics':[styledic]}]})
