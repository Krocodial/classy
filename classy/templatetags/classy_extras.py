from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
	return dictionary.get(str(key))

@register.filter
def multiply(value, arg):
    return value*arg

@register.filter
def replace_font(value):
    value = value.replace('<font color="green">', '<font color="green">')
    return value
