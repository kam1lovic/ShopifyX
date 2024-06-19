import re

from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.forms import ModelForm, CharField, Form, PasswordInput, TextInput, ModelChoiceField

from apps.models import Order, User, Stream, Product, Payment
from apps.validators import phone_regex


class OrderModelForm(ModelForm):
    product = ModelChoiceField(queryset=Product.objects.all())
    stream = ModelChoiceField(queryset=Stream.objects.all(), required=False)

    class Meta:
        model = Order
        fields = ('name', 'phone_number', 'product', 'stream')

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number and phone_number.startswith('+998'):
            phone_number = phone_number[4:].replace('(', '').replace(')', '').replace('-', '').replace(' ', '')
            return phone_number
        return phone_number


class LoginForm(Form):
    phone = CharField(label='Phone Number', widget=TextInput(attrs={'class': 'form-control'}), validators=[phone_regex])
    password = CharField(label='Password', widget=PasswordInput(attrs={'class': 'form-control'}))

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        phone = re.sub(r'\D', '', phone)
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


class UserProfileImageModelForm(ModelForm):
    class Meta:
        model = User
        fields = ('avatar',)


class UserPasswordModelForm(ModelForm):
    new_password1 = CharField(
        label='New password',
        widget=PasswordInput(attrs={'class': 'form-control'}),
    )
    new_password2 = CharField(
        label='Confirm new password',
        widget=PasswordInput(attrs={'class': 'form-control'}),
    )

    class Meta:
        model = User
        fields = ('password', 'new_password1', 'new_password2')


class StreamForm(ModelForm):
    product = ModelChoiceField(queryset=Product.objects.all())

    class Meta:
        model = Stream
        fields = ('name', 'discount', 'benefit', 'product')


class PaymentForm(ModelForm):
    class Meta:
        model = Payment
        fields = ('card_number', 'amount')
