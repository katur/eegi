from django import forms


class BlankNullBooleanSelect(forms.NullBooleanSelect):
    def __init__(self, attrs=None):
        choices = ((u'1', u''),
                   (u'3', u'No'),
                   (u'2', u'Yes'))
        forms.Select.__init__(self, attrs, choices)
