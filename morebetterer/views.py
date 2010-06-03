from django.shortcuts import render_to_response
from morebetterer.models import Item, Challenge
from django.core.paginator import Paginator, InvalidPage, EmptyPage

def top(request):
    topitems = Item.objects.topitems()
    paginator = Paginator(topitems, 20)
    
    # Make sure page request is an int. If not, deliver first page.
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    # If page request (9999) is out of range, deliver last page of results.
    try:
        items = paginator.page(page)
    except (EmptyPage, InvalidPage):
        items = paginator.page(paginator.num_pages)
        
    return render_to_response('top.html', {'items': items})
    
def challenge(request):
    item1, item2 = Item.objects.candidateitems()
    return render_to_response('challenge.html', {'item1': item1, 'item2' : item2})
    