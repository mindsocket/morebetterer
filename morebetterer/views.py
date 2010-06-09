from django.shortcuts import get_object_or_404,render_to_response
from django.template import RequestContext
from models import Item, Challenge
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.core.cache import cache
from base64 import urlsafe_b64encode, urlsafe_b64decode
from django.http import Http404
import hashlib
from django.conf import settings

def top(request):
    threshold = 1
    cachemins = 10
    topitems = cache.get('topitems'+str(threshold),Item.objects.topitems(threshold))
    cache.add('topitems'+str(threshold), topitems, cachemins * 60)
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
        
    return render_to_response('top.html', {'items': items, 'threshold': threshold, 'cachemins': cachemins},context_instance=RequestContext(request))
    
def challenge(request):
    ipaddress = request.META['REMOTE_ADDR']  
    
    if request.method == 'POST':
        left = request.POST['left']
        right = request.POST['right']
        expectedtoken = sign(left + ":" + right + ":" + ipaddress, settings.SECRET_KEY)
        if not request.POST['token'] == expectedtoken:
            raise Http404 

        choice = request.POST['choice']
        winner = left if choice == 'left' else right  
        loser = right if choice == 'left' else left
        
        challenge = Challenge(winner = get_object_or_404(Item, id=winner), loser = get_object_or_404(Item, id=loser), ipaddress = ipaddress)
        challenge.save()
        
    item1, item2 = Item.objects.candidateitems()
    token = sign(str(item1.id) + ":" + str(item2.id) + ":" + ipaddress, settings.SECRET_KEY)
    return render_to_response('challenge.html', {'item1': item1, 'item2': item2, 'token': token},context_instance=RequestContext(request))
    
def about(request):
    return render_to_response('about.html',context_instance=RequestContext(request))
    
def sign(s, key):
    return uri_b64encode(hashlib.sha1(s + ':'  + key).digest())

def uri_b64encode(s):
     return urlsafe_b64encode(s).strip('=')
