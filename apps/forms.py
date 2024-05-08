import re

from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.forms import ModelForm, CharField, Form, PasswordInput, TextInput, ModelChoiceField

from apps.models import Order, User, Stream, Product
from apps.validators import phone_regex


class OrderModelForm(ModelForm):
    class Meta:
        model = Order
        fields = ('id', 'name', 'phone_number', 'product')


class LoginForm(Form):
    phone = CharField(label='Phone Number', widget=TextInput(attrs={'class': 'form-control'}), validators=[phone_regex])
    password = CharField(label='Password', widget=PasswordInput(attrs={'class': 'form-control'}))

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        phone = re.sub(r'\D', '', phone)  # Faqat raqamlarni qoldirish
        return phone[3:]

    def clean(self):
        phone = self.cleaned_data.get("phone")
        password = self.cleaned_data.get("password")

        if phone and password:
            self.user_cache = authenticate(phone=phone, password=password)
            if self.user_cache is None:
                raise ValidationError("Invalid phone number or password")
        return self.cleaned_data

    def get_user(self):
        return self.user_cache


class UserProfileModelForm(ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'region', 'city', 'address', 'telegram_id', 'bio')


class StreamForm(ModelForm):
    product = ModelChoiceField(queryset=Product.objects.all())

    class Meta:
        model = Stream
        fields = ['name', 'product']
