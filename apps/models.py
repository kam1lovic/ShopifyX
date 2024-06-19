from django.contrib.auth.models import AbstractUser
from django.db.models import Model, CharField, ImageField, DecimalField, ForeignKey, CASCADE, DateTimeField, \
    ManyToManyField, PositiveBigIntegerField, PositiveIntegerField, TextChoices, TextField, IntegerField, SlugField, \
    DO_NOTHING, BigIntegerField, Manager, BooleanField
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django_ckeditor_5.fields import CKEditor5Field
from django_resized import ResizedImageField

from apps.managers import CustomUserManager


class BaseTimeModel(Model):
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class User(AbstractUser):
    class Type(TextChoices):
        ADMIN = 'admin', 'Admin'
        OPERATOR = 'operator', 'Operator'
        CURRIER = 'currier', 'Currier'
        USERS = 'user', 'User'
        MANAGER = 'manager', 'Manager'

    username = None
    avatar = ResizedImageField(size=[162, 162], upload_to='user/avatar')
    phone = CharField(max_length=20, unique=True)
    type = CharField(max_length=15, choices=Type.choices, default=Type.USERS)
    bio = TextField(max_length=300, null=True, blank=True)
    region = CharField(max_length=50, null=True, blank=True)
    city = CharField(max_length=50, null=True, blank=True)
    address = CharField(max_length=150, null=True, blank=True)
    telegram_id = BigIntegerField(null=True, blank=True, unique=True)
    balance = PositiveBigIntegerField(default=0)

    objects = CustomUserManager()

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = []

    def clean(self, *args, **kwargs):
        if self.phone.startswith('+998'):
            phone_number = self.phone[4:]
            phone_number = phone_number.replace('(', '').replace(')', '').replace('-', '').replace(' ', '')
            self.phone = phone_number
            return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        for field_name in ['avatar']:
            field = getattr(self, field_name)
            if field:
                field.storage.delete(field.path)

        super(User, self).delete(*args, **kwargs)

    @property
    def count_wishlist(self):
        return self.wishlist_set.count()

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')


class TypeUserManager(Manager):
    def for_type(self, type):
        return self.get_queryset().filter(type=type)


class AdminUserManager(TypeUserManager):
    def get_queryset(self):
        return super().get_queryset().filter(type=User.Type.ADMIN)


class AdminUser(User):
    objects = AdminUserManager()

    class Meta:
        proxy = True
        verbose_name = _('Admin User')
        verbose_name_plural = _('Admin Users')


class OperatorUserManager(TypeUserManager):
    def get_queryset(self):
        return super().get_queryset().filter(type=User.Type.OPERATOR)


class OperatorUser(User):
    objects = OperatorUserManager()

    class Meta:
        proxy = True
        verbose_name = _('Operator User')
        verbose_name_plural = _('Operator Users')


class CourierUserManager(TypeUserManager):
    def get_queryset(self):
        return super().get_queryset().filter(type=User.Type.CURRIER)


class CourierUser(User):
    objects = CourierUserManager()

    class Meta:
        proxy = True
        verbose_name = _('Courier User')
        verbose_name_plural = _('Courier Users')


class RegularUserManager(TypeUserManager):
    def get_queryset(self):
        return super().get_queryset().filter(type=User.Type.USERS)


class RegularUser(User):
    objects = RegularUserManager()

    class Meta:
        proxy = True
        verbose_name = _('Regular User')
        verbose_name_plural = _('Regular Users')


class ManagerUserManager(TypeUserManager):
    def get_queryset(self):
        return super().get_queryset().filter(type=User.Type.MANAGER)


class ManagerUser(User):
    objects = ManagerUserManager()

    class Meta:
        proxy = True
        verbose_name = _('Manager User')
        verbose_name_plural = _('Manager Users')


class Category(BaseTimeModel):
    name = CharField(max_length=100)
    image = ImageField(upload_to='category/')
    slug = SlugField(max_length=100, unique=True, editable=False)

    def __str__(self):
        return self.name

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.slug = slugify(self.name)
        super().save(force_insert, force_update, using, update_fields)

    def delete(self, *args, **kwargs):
        self.image.delete()
        super().delete(*args, **kwargs)

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')


class Tag(BaseTimeModel):
    name = CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Tag')
        verbose_name_plural = _('Tags')


class Product(BaseTimeModel):
    name = CharField(max_length=255)
    slug = SlugField(max_length=100, unique=True, editable=False)
    description = CKEditor5Field()
    author = ForeignKey('apps.User', on_delete=CASCADE)
    short_description = CKEditor5Field(max_length=500)
    price = DecimalField(max_digits=20, decimal_places=1)
    discount = CharField(max_length=60, null=True, blank=True, default='yo\'q')
    user_payment = PositiveIntegerField(default=30000,
                                        verbose_name='Maxsulot sotilgandan so\'ng userga beriladigan summa')
    quantity = PositiveBigIntegerField(default=1)
    category = ForeignKey('apps.Category', on_delete=CASCADE, to_field='slug', related_name='products')
    tag = ManyToManyField('apps.Tag')

    def __str__(self):
        return self.name

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.slug = slugify(self.name)
        super().save(force_insert, force_update, using, update_fields)

    @property
    def first_image(self):
        return self.productimage_set.first()

    class Meta:
        ordering = ['-id']
        verbose_name = _('Product')
        verbose_name_plural = _('Products')

    def delete(self, *args, **kwargs):
        for image in self.productimage_set.all():
            storage, path = image.image.storage, image.image.path
            storage.delete(path)
            image.delete()
        super(Product, self).delete(*args, **kwargs)


class ProductImage(BaseTimeModel):
    image = ImageField(upload_to='products/')
    product = ForeignKey('apps.Product', CASCADE)

    def __str__(self):
        return f'{self.id}'

    class Meta:
        verbose_name = _('Product image')
        verbose_name_plural = _('Product images')


class Order(BaseTimeModel):
    class Status(TextChoices):
        NEW = 'new', 'New'
        VISIT = 'visit', 'Visit'
        READY = 'ready', 'Ready'
        DELIVERY = 'delivery', 'Delivery'
        DELIVERED = 'delivered', 'Delivered'
        CANCELLED = 'cancelled', 'Cancelled'
        ARCHIVED = 'archived', 'Archived'
        MISSED_CALL = 'missed_call', 'Missed Call'

    referral_user = ForeignKey('apps.User', CASCADE, related_name='referral', blank=True, null=True,
                               verbose_name='Referral user')
    image = ResizedImageField(size=[60, 39], upload_to='order/', null=True, blank=True)
    status = CharField(max_length=30, choices=Status.choices, default=Status.NEW)
    quantity = PositiveIntegerField(default=1)
    name = CharField(max_length=20)
    phone_number = CharField(max_length=20)
    product = ForeignKey('apps.Product', CASCADE, to_field='slug', related_name='products')
    currier = ForeignKey('apps.User', CASCADE, limit_choices_to={'type': User.Type.CURRIER}, null=True, blank=True)
    district = ForeignKey('apps.District', CASCADE, verbose_name='District', blank=True, null=True)
    stream = ForeignKey('apps.Stream', CASCADE, verbose_name='stream', related_name='orders', blank=True, null=True)
    operator = ForeignKey('apps.User', CASCADE, related_name='operator_orders', blank=True, null=True,
                          verbose_name='Operator')
    comment = CharField(max_length=255, blank=True, null=True)
    street = CharField(max_length=25, verbose_name="Street", blank=True, null=True)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.slug = slugify(self.name)
        super().save(force_insert, force_update, using, update_fields)

        if self.status == self.Status.DELIVERED and self.referral_user:
            self.referral_user.balance += self.product.user_payment
            self.referral_user.save()

    def __str__(self):
        return f"Order #{self.pk} - {self.product.name}"

    class Meta:
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')


class StatusOrderManager(Manager):
    def for_status(self, status):
        return self.get_queryset().filter(status=status)


class NewOrderManager(StatusOrderManager):
    def get_queryset(self):
        return super().get_queryset().filter(status=Order.Status.NEW)


class NewOrder(Order):
    objects = NewOrderManager()

    class Meta:
        proxy = True
        verbose_name = _('New Order')
        verbose_name_plural = _('New Orders')


class VisitOrderManager(StatusOrderManager):
    def get_queryset(self):
        return super().get_queryset().filter(status=Order.Status.VISIT)


class VisitOrder(Order):
    object = VisitOrderManager()

    class Meta:
        proxy = True
        verbose_name = _('Visit Order')
        verbose_name_plural = _('Visit Orders')


class ReadyOrderManager(StatusOrderManager):
    def get_queryset(self):
        return super().get_queryset().filter(status=Order.Status.READY)


class ReadyOrder(Order):
    object = ReadyOrderManager()

    class Meta:
        proxy = True
        verbose_name = _('Ready Order')
        verbose_name_plural = _('Ready Orders')


class DeliveryOrderManager(StatusOrderManager):
    def get_queryset(self):
        return super().get_queryset().filter(status=Order.Status.DELIVERY)


class DeliveryOrder(Order):
    object = DeliveryOrderManager()

    class Meta:
        proxy = True
        verbose_name = _('Delivery Order')
        verbose_name_plural = _('Delivery Orders')


class DeliveredOrderManager(StatusOrderManager):
    def get_queryset(self):
        return super().get_queryset().filter(status=Order.Status.DELIVERED)


class DeliveredOrder(Order):
    object = DeliveredOrderManager()

    class Meta:
        proxy = True
        verbose_name = _('Delivered Order')
        verbose_name_plural = _('Delivered Orders')


class CancelledOrderManager(StatusOrderManager):
    def get_queryset(self):
        return super().get_queryset().filter(status=Order.Status.CANCELLED)


class CancelledOrder(Order):
    object = CancelledOrderManager()

    class Meta:
        proxy = True
        verbose_name = _('Cancelled Order')
        verbose_name_plural = _('Cancelled Orders')


class ArchivedOrderManager(StatusOrderManager):
    def get_queryset(self):
        return super().get_queryset().filter(status=Order.Status.ARCHIVED)


class ArchivedOrder(Order):
    object = ArchivedOrderManager()

    class Meta:
        proxy = True
        verbose_name = _('Archived Order')
        verbose_name_plural = _('Archived Orders')


class MissedCallOrderManager(StatusOrderManager):
    def get_queryset(self):
        return super().get_queryset().filter(status=Order.Status.MISSED_CALL)


class MissedCallOrder(Order):
    object = MissedCallOrderManager()

    class Meta:
        proxy = True
        verbose_name = _('Missed Call Order')
        verbose_name_plural = _('Missed Call Orders')


class Region(BaseTimeModel):
    name = CharField(max_length=30)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Region')
        verbose_name_plural = _('Regions')


class District(BaseTimeModel):
    name = CharField(max_length=30)
    region = ForeignKey('apps.Region', CASCADE)

    class Meta:
        verbose_name = _('District')
        verbose_name_plural = _('Districts')

    def __str__(self):
        return self.name


class Stream(BaseTimeModel):
    name = CharField(max_length=50, null=True, blank=True)
    discount = BigIntegerField(null=True, blank=True)
    benefit = BigIntegerField(null=True, blank=True)
    count = IntegerField(default=0)
    product = ForeignKey('apps.Product', CASCADE)
    owner = ForeignKey('apps.User', CASCADE, null=True, blank=True)

    class Meta:
        verbose_name = _('Stream')
        verbose_name_plural = _('Streams')


class Wishlist(BaseTimeModel):
    user = ForeignKey('apps.User', on_delete=CASCADE, null=True)
    product = ForeignKey('apps.Product', on_delete=DO_NOTHING)

    def __str__(self):
        return self.product.name

    class Meta:
        verbose_name = _('Wishlist')
        verbose_name_plural = _('Wishlists')


class Competition(BaseTimeModel):
    title = CharField(max_length=50)
    image = ImageField(upload_to='competitions/', null=True, blank=True)
    description = CKEditor5Field(null=True, blank=True)
    is_active = BooleanField(default=False)
    start_date = DateTimeField(null=True, blank=True)
    end_date = DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _('Competition')
        verbose_name_plural = _('Competitions')


class SiteSettings(BaseTimeModel):
    delivery_cost = BigIntegerField(default=30000)

    class Meta:
        verbose_name = _('Site Setting')
        verbose_name_plural = _('Site Settings')


class Payment(Model):
    class Status(TextChoices):
        PROGRESS = 'progress', 'Progress'
        CANCELLED = 'cancelled', 'Cancelled'
        PAID = 'paid', 'Paid'

    user = ForeignKey('apps.User', CASCADE)
    card_number = CharField(max_length=16)
    amount = PositiveIntegerField(default=0)
    message = TextField(null=True, blank=True)
    status = CharField(max_length=30, choices=Status.choices, default=Status.PROGRESS)
    created_at = DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Payment')
        verbose_name_plural = _('Payments')
