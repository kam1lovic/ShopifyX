from django import template

register = template.Library()


@register.filter()
def get_base_url(url: str):
    absolute_uri = url.split('/')[:3]
    return '/'.join(absolute_uri)
