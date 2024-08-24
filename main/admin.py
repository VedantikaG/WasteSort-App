from django.contrib import admin

from main.models import ScmsUser, ScmsComplaint


# Register your models here.
@admin.register(ScmsUser)
class ScmsUserAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'u_username',
        'is_admin',
    ]

    search_fields = [
        'u_username',
    ]

    list_filter = [
        'is_admin',
    ]

    list_display_links = [
        'id',
        'u_username',
    ]


@admin.register(ScmsComplaint)
class ScmsComplaintAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'c_title',
        'c_verified',
        'c_resolved',
        'c_datetime',
        'reporter',
    ]

    def reporter(self, obj):
        return obj.u_id.u_username

    search_fields = [
        'c_title',
    ]

    list_filter = [
        'c_verified',
        'c_resolved',
        'c_datetime',
    ]

    list_display_links = [
        'id',
        'c_title',
    ]
