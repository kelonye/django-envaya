from django.contrib import admin
from models import InboxMessage, OutboxMessage

class InboxAdmin(admin.ModelAdmin):
    list_display = [
          'date_received'
        , 'from'
        , 'message'
    ]

class OutboxAdmin(admin.ModelAdmin):
    list_display = [
         'date_sent'
        , 'to'
        , 'message'
        , 'send_status'
        , 'send_error'
    ]

admin.site.register(InboxMessage, InboxAdmin)
admin.site.register(OutboxMessage, OutboxAdmin)
