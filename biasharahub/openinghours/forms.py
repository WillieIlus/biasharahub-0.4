from datetime import time

from django import forms
from django.forms import ModelForm, TimeInput

from openinghours.models import OpeningHours, WEEKDAYS


def str_to_time(s):
    """ Turns strings like '08:30' to time objects """
    return time(*[int(x) for x in s.split(':')])


def time_to_str(t):
    """ Turns time objects to strings like '08:30' """
    return t.strftime('%H:%M')


def time_choices():
    """Return digital time choices every half hour from 00:00 to 23:30."""
    hours = list(range(0, 24))
    times = []
    for h in hours:
        hour = str(h).zfill(2)
        times.append(hour + ':00')
        times.append(hour + ':30')
    return list(zip(times, times))


TIME_CHOICES = time_choices()


class Slot(forms.Form):
    opens = forms.ChoiceField(choices=TIME_CHOICES)
    shuts = forms.ChoiceField(choices=TIME_CHOICES)


class OpeningHoursForm(ModelForm):
    weekday = forms.ChoiceField(required=False, choices=WEEKDAYS)
    start = forms.TimeField(input_formats=['%H:%M'], label='Opening', required=False,
                            widget=forms.TimeInput(attrs={'type': 'time'}))
    end = forms.TimeField(input_formats=['%H:%M'], label='Closing', required=False,
                            widget=forms.TimeInput(attrs={'type': 'time'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['weekday']
        # self.fields['weekday'].disabled = disabled_weekday

    class Meta:
        model = OpeningHours
        fields = ('weekday', 'start', 'end', 'closed')
        widget = {
            'start': TimeInput(attrs={'type': 'time'}),
            'start': TimeInput(attrs={'type': 'time'})
        }

# formset = OpeningHoursFormset(initial=[{'weekday': x} for x in OpeningHours.weekday.choices])

#
# class OpeningHoursFormsetHelper(FormHelper):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         # self.helper = FormHelper()
#         self.form_class = 'form-inline'
#         self.field_template = 'bootstrap4/layout/inline_field.html'
#         self.layout = Layout(
#             Row(
#                 Column('weekday', readonly=True, css_class='atbd_day_label form-label col-md-3 mb-1'),
#                 Column('start', css_class='directory_field col-md-4 mb-1'),
#                 Column('end', css_class=' directory_field col-md-4 mb-1'),
#                 Column('closed', css_class='custom-control-label col-md-1 mb-1'),
#             ),
#             self.add_input(Submit("submit", "Save", css_class='btn btn-gradient'))
#         )
