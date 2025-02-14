from django.contrib import admin
from django.contrib.admin.models import LogEntry
from .models import InventoryItem, Category, Drug, Transaction, Unit, Site, UserProfile, \
    SafetyStock, InventoryInspection, DrugObsoleteBySite

title = 'CK-Stock 管理サイト'

admin.site.site_header = title
admin.site.site_title = title
admin.site.index_title = title


@admin.register(Drug)
class DrugAdmin(admin.ModelAdmin):
    list_display = (
        "id", "name", "kana", "category", "unit", "obsoleted", "date_created", "user")
    search_fields = ["name", "kana"]


@admin.register(DrugObsoleteBySite)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "drug", "site", "is_obsolete")
    search_fields = ["drug__name"]


@admin.register(SafetyStock)
class SafetyStockAdmin(admin.ModelAdmin):
    list_display = ("id", "drug", "site", "min_stock")
    search_fields = ["drug__name", "site__name"]


@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = (
        "id", "name", "quantity", "unit", "lot", "expire_date", "site", "date_created", "user")
    search_fields = ["name__name", "lot"]


@admin.register(InventoryInspection)
class InventoryInspectionAdmin(admin.ModelAdmin):
    list_display = (
        "id", "site", "inventory_adjusted", "date_created", "user")
    search_fields = ["site__name"]


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        "id", "type", "status", "name", "quantity", "unit", "lot", "expire_date", "source_site", "dest_site",
        "date_created", "user")
    search_fields = ["name__name", "lot", "source_site__name", "dest_site__name"]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "obsoleted", "date_created", "user")
    search_fields = ["name"]


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "date_created", "user")
    search_fields = ["name"]


@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "address", "obsoleted", "date_created", "user")
    search_fields = ["name"]


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "scanner_mode_enabled", "default_site")
    search_fields = ["user__username"]


@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    date_hierarchy = 'action_time'

    list_filter = [
        'user',
        'content_type',
        'action_flag'
    ]

    search_fields = [
        'object_repr',
        'change_message',
        'user__username',
        'content_type__model',
    ]

    list_display = [
        'action_time',
        'user',
        'content_type',
        'action_flag',
    ]
