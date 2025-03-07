from django import template

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css):
    return field.as_widget(attrs={"class": css})


@register.simple_tag
def range_1_32():
    return range(1, 32)  # Genera los números del 1 al 31