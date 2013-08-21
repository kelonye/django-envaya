from django.contrib import admin
from models import InboxMessage, OutboxMessage

class InboxAdmin(admin.ModelAdmin):
    list_display = [
          'date_received'
        , 'phone_number'
        , 'action'
    ]

class OutboxAdmin(admin.ModelAdmin):
    list_display = [
         'date_sent'
        , 'to'
        , 'message'
        , 'status'
    ]

    def status(self, msg):
        if not msg.send_status:
            return
        return msg.send_status.status

admin.site.register(InboxMessage, InboxAdmin)
admin.site.register(OutboxMessage, OutboxAdmin)
