from django.shortcuts import render_to_response
from morebetterer.models import Item, Challenge

def top(request):
    items = Item.objects.topitems()
    return render_to_response('top.html', {'items': items})
    
def challenge(request):
    item1, item2 = Item.objects.candidateitems()
    return render_to_response('challenge.html', {'item1': item1, 'item2' : item2})
    