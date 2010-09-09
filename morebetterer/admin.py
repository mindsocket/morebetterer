from morebetterer.models import Item, Challenge, ChallengeCount
from django.contrib import admin
from convert.base import MediaFile
from convert.conf import settings

class ChallengeWinnerInline(admin.TabularInline):
    model = Challenge
    fk_name = 'winner'
    extra = 0

class ChallengeLoserInline(admin.TabularInline):
    model = Challenge
    fk_name = 'loser'
    extra = 0

class ChallengeAdmin(admin.ModelAdmin):
    date_hierarchy = 'timestamp'
    list_display = ('__unicode__', 'ipaddress', 'timestamp')
    search_fields = ['ipaddress']
    list_filter = ('timestamp',)

class ChallengeCountAdmin(admin.ModelAdmin):
    list_display = ('ipaddress', 'count')

class ItemAdmin(admin.ModelAdmin):
    list_display = ('itemname', 'itemimgimg', 'wincount', 'challengecount')
    search_fields = ['itemname']
    inlines = [ ChallengeWinnerInline, ChallengeLoserInline, ]
    def itemimgimg(self,item):
      img=MediaFile(item.itemimg)
      thumb=img.thumbnail("64x64gt")
      return thumb.tag
    itemimgimg.allow_tags = True

admin.site.register(Item, ItemAdmin)
admin.site.register(Challenge, ChallengeAdmin)
admin.site.register(ChallengeCount, ChallengeCountAdmin)

