from django.contrib import admin
from .models import LoginHistory, BlockedNetwork, BlockedIP, PendingEmailChange
from rangefilter.filters import DateRangeFilter

# Classe de admin opcional para BlockedNetwork
class BlockedNetworkAdmin(admin.ModelAdmin):
	list_display = ('network', 'timestamp')
	search_fields = ('network',)

# Classe de admin opcional para BlockedIP
class BlockedIPAdmin(admin.ModelAdmin):
	list_display = ('ip_address', 'timestamp')
	search_fields = ('ip_address',)

# Classe de admin opcional para LoginHistory
class LoginHistoryAdmin(admin.ModelAdmin):
	list_display = ('user', 'ip_address', 'country', 'city', 'timestamp')
	list_filter = ('user', 'country', 'timestamp')
	search_fields = ('ip_address', 'city')

# Classe de admin opcional para pedencias
class PendingEmailChangeAdmin(admin.ModelAdmin):
	list_display = ('user', 'new_email', 'created_at', 'expires_at', 'confirmation_token')
	search_fields = ('user__username', 'new_email')

#admin.site.register(LoginHistory)
admin.site.register(BlockedIP, BlockedIPAdmin)
admin.site.register(BlockedNetwork, BlockedNetworkAdmin)
admin.site.register(LoginHistory, LoginHistoryAdmin)
admin.site.register(PendingEmailChange, PendingEmailChangeAdmin)