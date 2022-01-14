from django.contrib import admin

from .models import school
from .models import tag
from .models import epoch
from .models import access_control

admin.site.register(school)
admin.site.register(tag)
admin.site.register(epoch)
admin.site.register(access_control)
