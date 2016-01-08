"""Utility module with Django form helpers."""

from collections import OrderedDict

from django import forms
from django.template.loader import render_to_string


EMPTY_CHOICE = ('', '---------')


def reorder_fields(obj, key_order):
    """
    Reorder obj.fields in the order determined by key_order.

    Use this function to set the field order for a forms.Form object.
    (NOTE: While the field order can be changed for a forms.ModelForm by
    setting the Meta 'fields' option, this does not work for a forms.Form.)
    """
    original_fields = obj.fields
    new_fields = OrderedDict()
    for key in key_order:
        new_fields[key] = original_fields[key]
    obj.fields = new_fields


class BlankNullBooleanSelect(forms.NullBooleanSelect):
    def __init__(self, attrs=None):
        choices = ((u'1', u'---'),
                   (u'3', u'No'),
                   (u'2', u'Yes'))
        forms.Select.__init__(self, attrs, choices)


class RangeWidget(forms.MultiWidget):
    def __init__(self, widget, *args, **kwargs):
        widgets = (widget, widget)

        super(RangeWidget, self).__init__(widgets=widgets,
                                          *args, **kwargs)

    def decompress(self, value):
        return value

    def format_output(self, rendered_widgets):
        context = {'min': rendered_widgets[0], 'max': rendered_widgets[1]}
        return render_to_string('widgets/range_widget.html', context)


class RangeField(forms.MultiValueField):
    """
    A field with min and max fields.

    Pass field_class when initializing to define the type of the
    min and max subfields.

    Optionally pass widget_class while initializing to define the
    type of the min and max widgets.
    """
    def __init__(self, field_class, field_kwargs={}, *args, **kwargs):
        # Initialize both min/max to blank
        if not 'initial' in kwargs:
            kwargs['initial'] = ['','']

        # Define min/max pair of fields
        fields = (field_class(**field_kwargs), field_class(**field_kwargs))

        # Use default field_class widget
        widget = RangeWidget(field_class().widget)

        super(RangeField, self).__init__(fields=fields, widget=widget,
                                         *args, **kwargs)

    def compress(self, data_list):
        if data_list:
            return [self.fields[0].clean(data_list[0]),
                    self.fields[1].clean(data_list[1])]

        return None
