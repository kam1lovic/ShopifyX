from django.core.validators import RegexValidator

phone_regex = RegexValidator(
    regex=r'^\+998\(\d{2}\)\s\d{3}-\d{2}-\d{2}$',
    message="Phone number must contain only digits and be in string format."
)
