from django.contrib import admin
from .models import Comment, BlockedIP

class BlockedIPAdmin(admin.ModelAdmin):
	list_display = ('ip_address', 'timestamp')
	search_fields = ('ip_address',)

admin.site.register(Comment)
admin.site.register(BlockedIP, BlockedIPAdmin)