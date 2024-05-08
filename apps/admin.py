from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from django.contrib.admin import ModelAdmin, StackedInline
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from apps.models import Product, ProductImage, Category, Tag, Order, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    ordering = ['first_name']
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "email", "avatar", "banner")}),
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


@admin.register(Order)
class OrderModelAdmin(ModelAdmin):
    pass


admin.site.unregister(Group)
