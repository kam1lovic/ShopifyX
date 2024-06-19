from django.contrib import admin
from django.contrib.admin import ModelAdmin, StackedInline
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _

from apps.models import Product, ProductImage, Category, Tag, Order, User, NewOrder, VisitOrder, ReadyOrder, \
    DeliveryOrder, DeliveredOrder, CancelledOrder, ArchivedOrder, MissedCallOrder, AdminUser, CourierUser, OperatorUser, \
    RegularUser, ManagerUser, SiteSettings, Competition, Payment


@admin.register(User)
class CustomUserAdmin(ModelAdmin):
    ordering = ('id',)
    fieldsets = (
        (None, {"fields": ("password",)}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "email", "avatar", "phone")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )


@admin.register(AdminUser)
class AdminUser(ModelAdmin):
    pass


@admin.register(CourierUser)
class CurrierUser(ModelAdmin):
    pass


@admin.register(OperatorUser)
class OperatorUser(ModelAdmin):
    pass


@admin.register(RegularUser)
class RegularUser(ModelAdmin):
    pass


@admin.register(ManagerUser)
class ManagerUser(ModelAdmin):
    pass


@admin.register(NewOrder)
class NewOrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'status', 'phone_number', 'product']


@admin.register(VisitOrder)
class VisitOrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'status', 'phone_number', 'product']


@admin.register(ReadyOrder)
class ReadyOrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'status', 'phone_number', 'product']


@admin.register(DeliveryOrder)
class DeliveryOrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'status', 'phone_number', 'product']


@admin.register(DeliveredOrder)
class DeliveredOrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'status', 'phone_number', 'product']


@admin.register(CancelledOrder)
class CancelledOrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'status', 'phone_number', 'product']


@admin.register(ArchivedOrder)
class ArchivedOrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'status', 'phone_number', 'product']


@admin.register(MissedCallOrder)
class MissedCallOrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'status', 'phone_number', 'product']


class ProductImageStackedInline(StackedInline):
    model = ProductImage
    extra = 1
    min_num = 1


@admin.register(Category)
class CategoryModelAdmin(ModelAdmin):
    pass


@admin.register(Tag)
class TagModelAdmin(ModelAdmin):
    pass


@admin.register(Product)
class ProductModelAdmin(ModelAdmin):
    inlines = [ProductImageStackedInline]


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return super().has_delete_permission(request, obj)


@admin.register(Order)
class OrderModelAdmin(ModelAdmin):
    pass


@admin.register(Competition)
class CompetitionModelAdmin(ModelAdmin):
    pass


@admin.register(Payment)
class PaymentModelAdmin(ModelAdmin):
    pass


def get_app_list(self, request):
    custom_order = [
        _('New Orders'),
        _('Visit Orders'),
        _('Ready Orders'),
        _('Delivery Orders'),
        _('Delivered Orders'),
        _('Cancelled Orders'),
        _('Missed Call Orders'),
        _('Archived Orders'),
        _('Courier Users'),
        _('Operator Users'),
        _('Manager Users'),
        _('Admin Users'),
        _('Users'),
        _('Regular Users'),
        _('Orders'),
        _('Products'),
        _('Payments'),

        _('Product Images'),
        _('Categories'),
        _('Competitions'),
        _('Regions'),
        _('Districts'),
        _('Tags'),
        _('Site Settings')
    ]

    app_dict = self._build_app_dict(request)
    app_list = sorted(app_dict.values(), key=lambda x: x['name'].lower())
    for app in app_list:
        if app['app_label'] == 'apps':
            app['models'].sort(key=lambda x: custom_order.index(x['name']))
    return app_list


admin.AdminSite.get_app_list = get_app_list

admin.site.unregister(Group)
