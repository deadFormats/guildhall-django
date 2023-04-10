from django import forms
from django import template
from django.forms import BoundField
from django.template.loader import get_template
from django.utils.safestring import mark_safe


register = template.Library()


@register.simple_tag
def font_awesome():
    cdn_link = '<link rel="stylesheet" '
    cdn_link += 'href="https://use.fontawesome.com/releases/v5.7.2/css/all.css" '
    cdn_link += 'integrity="sha384-fnmOCqbTlWIlj8LyTjo7mOUStjsKC4pOpQbqyi7RrhN7udi9RwhKkMHpvLbHG9Sr" '
    cdn_link += 'crossorigin="anonymous">'
    return mark_safe(cdn_link)




@register.filter
def bulma_form(element):
    markup_classes = {
        'label': '',
        'value': '',
        'single_value': ''
    }
    return render(element, markup_classes)




@register.filter
def add_input_classes(field):
    if not is_checkbox(field) and not is_multiple_checkbox(field) and not is_radio(field) and not is_file(field):
        field_classes = field.field.widget.attrs.get('class', '')
        field_classes += ' control'
        field.field.widget.attrs['class'] = field_classes



def render(element, markup_classes):
    if isinstance(element, BoundField):
        add_input_classes(element)
        template = get_template('forms/field.html')
        context = {'field': element, 'classes': markup_classes, 'form': element.form}
    else:
        has_management = getattr(element, 'management_form', None)
        if has_management:
            for form in element.forms:
                for field in form.visible_fields():
                    add_input_classes(field)

            template = get_template('forms/formset.html')
            context = {'formset': element, 'classes': markup_classes}

        else:
            for field in element.visible_fields():
                add_input_classes(field)

            template = get_template('forms/form.html')
            context = {'form': element, 'classes': markup_classes}

    return template.render(context)

@register.filter
def widget_type(field):
    return field.field.widget


@register.filter
def is_select(field):
    return isinstance(field.field.widget, forms.Select)


@register.filter
def is_multiple_select(field):
    return isinstance(field.field.widget, forms.SelectMultiple)


@register.filter
def is_textarea(field):
    return isinstance(field.field.widget, forms.Textarea)


@register.filter
def is_input(field):
    return isinstance(field.field.widget, (
        forms.TextInput,
        forms.NumberInput,
        forms.EmailInput,
        forms.PasswordInput,
        forms.URLInput
    ))


@register.filter
def is_checkbox(field):
    return isinstance(field.field.widget, forms.CheckboxInput)


@register.filter
def is_multiple_checkbox(field):
    return isinstance(field.field.widget, forms.CheckboxSelectMultiple)


@register.filter
def is_radio(field):
    return isinstance(field.field.widget, forms.RadioSelect)


@register.filter
def is_file(field):
    return isinstance(field.field.widget, forms.FileInput)


@register.filter
def addclass(field, css_class):
    if len(field.errors) > 0:
        css_class += ' is-danger'
    field_classes = field.field.widget.attrs.get('class', '')
    field_classes += f' {css_class}'
    return field.as_widget(attrs={"class": field_classes})



@register.filter
def bulma_message_tag(tag):
    return {
        'error': 'danger'
    }.get(tag, tag)
