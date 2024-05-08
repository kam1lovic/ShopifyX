from django.contrib.auth.models import AbstractUser
from django.db.models import Model, CharField, ImageField, DecimalField, ForeignKey, CASCADE, DateTimeField, \
    ManyToManyField, PositiveBigIntegerField, PositiveIntegerField, TextChoices, TextField, IntegerField, SlugField, \
    DO_NOTHING
from django.utils.text import slugify
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
    banner = ResizedImageField(size=[162, 162], upload_to='user/banner')
    phone = CharField(max_length=20, unique=True)
    type = CharField(max_length=15, choices=Type.choices, default=Type.USERS)
    bio = TextField(max_length=300, null=True, blank=True)
    region = CharField(max_length=50, null=True, blank=True)
    city = CharField(max_length=50, null=True, blank=True)
    address = CharField(max_length=150, null=True, blank=True)
    telegram_id = IntegerField(null=True, blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = []

    def delete(self, *args, **kwargs):
        for field_name in ['avatar', 'banner']:
            field = getattr(self, field_name)
            if field:
                field.storage.delete(field.path)

        super(User, self).delete(*args, **kwargs)


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


class Tag(BaseTimeModel):
    name = CharField(max_length=100)

    def __str__(self):
        return self.name


class Product(BaseTimeModel):
    name = CharField(max_length=255)
    slug = SlugField(max_length=100, unique=True, editable=False)
    description = CKEditor5Field()
    author = ForeignKey('apps.User', on_delete=CASCADE)
    short_description = CKEditor5Field(max_length=350)
    price = DecimalField(max_digits=20, decimal_places=1)
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

    image = ResizedImageField(size=[60, 39], upload_to='order/', null=True, blank=True)
    status = CharField(max_length=30, choices=Status.choices, default=Status.NEW)
    quantity = PositiveIntegerField(default=1)
    name = CharField(max_length=20)
    phone_number = CharField(max_length=20)
    product = ForeignKey('apps.Product', CASCADE, to_field='slug')
    currier = ForeignKey('apps.User', CASCADE, limit_choices_to={'type': User.Type.CURRIER}, null=True, blank=True)
    comment = CharField(max_length=255, blank=True, null=True)
    district = ForeignKey('apps.District', CASCADE, verbose_name='District', blank=True, null=True)
    street = CharField(max_length=25, verbose_name="Street", blank=True, null=True)
    operator = ForeignKey('apps.User', CASCADE, related_name='operator_orders', blank=True, null=True,
                          verbose_name='Operator')
    stream = ForeignKey('apps.Stream', CASCADE, verbose_name='stream', related_name='orders', blank=True, null=True, )

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.slug = slugify(self.name)
        super().save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return f"Order #{self.pk} - {self.product.name}"


class Region(Model):
    name = CharField(max_length=30)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Region'
        verbose_name_plural = 'Regions'


class District(Model):
    name = CharField(max_length=30)
    region = ForeignKey('apps.Region', CASCADE)

    class Meta:
        verbose_name = 'District'
        verbose_name_plural = 'Districts'

    def __str__(self):
        return self.name


class Stream(Model):
    name = CharField(max_length=50, null=True, blank=True)
    count = IntegerField(default=0)
    product = ForeignKey('apps.Product', on_delete=CASCADE)
    user = ForeignKey('apps.User', on_delete=CASCADE)


class Wishlist(Model):
    user = ForeignKey('apps.User', on_delete=CASCADE, null=True)
    product = ForeignKey('apps.Product', on_delete=DO_NOTHING)

    def __str__(self):
        return self.product.name
