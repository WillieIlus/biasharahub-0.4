from builtins import super

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column, Layout, Row, Submit
from django import forms
# from django.contrib.admin import widgets
from django.forms import inlineformset_factory, ModelForm, modelformset_factory
from django.utils.translation import ugettext_lazy as _
from haystack.forms import FacetedSearchForm
from pagedown.widgets import PagedownWidget

from business.models import Business, BusinessImage, CompanySocialProfile
from categories.models import Category
from locations.models import Location
from reviews.models import RATING_CHOICES


class BusinessForm(ModelForm):
    logo = forms.ImageField(label='logo', required=False,
                            widget=forms.ClearableFileInput(attrs={'placeholder': 'Logo',
                                                                   'class': 'btn btn-outline-secondary'}))
    description = forms.CharField(widget=PagedownWidget())

    class Meta:
        model = Business
        fields = (
            'name', 'logo', 'email', 'description', 'website', 'location', 'category', 'address', 'services')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        self.helper.form_method = 'post'
        # self.helper.form_action = 'submit'
        # self.helper.add_input(Submit('submit', 'Submit', css_class='btn btn-gradient btn-gradient-two btn-lg'))
        self.helper.layout = Layout(
            'name',
            'logo',
            'email',
            'description',
            'website',
            'location',
            'category',
            'address',
            'services',
        )


class BusinessFilterForm(forms.Form):
    category = forms.ModelChoiceField(
        label=_("Category"), required=False, queryset=Category.objects.all(),
    )
    location = forms.ModelChoiceField(label=_("Location"), required=False, queryset=Location.objects.all(), )
    rating = forms.ChoiceField(label=_("Rating"), required=False, choices=RATING_CHOICES, )


class BusinessPhotoForm(ModelForm):
    class Meta:
        model = BusinessImage
        fields = ('img', 'alt')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            'img',
            'alt',
        )


BusinessPhotoFormSet = modelformset_factory(BusinessImage, form=BusinessPhotoForm, extra=6, max_num=12, can_delete=True)


class BusinessPhotoFormSetHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super(BusinessPhotoFormSetHelper, self).__init__(*args, **kwargs)
        self.form_method = 'post'
        self.layout = Layout(
            Row(
                Column('img', css_class='mt-10 form-group col-md-4 mb-0'),
                Column('alt', css_class='mt-10 form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
        )
        self.add_input(Submit("submit", "Save", css_class='btn btn-gradient btn-gradient-one'))


class SocialProfileForm(ModelForm):
    class Meta:
        model = CompanySocialProfile
        fields = ('network', 'username', 'url')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('network', css_class='mt-10 form-group col-md-3 mb-0'),
                Column('username', css_class='mt-10 form-group col-md-3 mb-0'),
                Column('url', css_class='mt-10 form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
        )


SocialProfileFormSet = inlineformset_factory(Business, CompanySocialProfile, form=SocialProfileForm,
                                             can_delete=True, extra=3)


class BusinessSearchForm(FacetedSearchForm):

    def __init__(self, *args, **kwargs):
        data = dict(kwargs.get("data", []))
        self.category = data.get('category', [])
        self.location = data.get('location', [])
        super(BusinessSearchForm, self).__init__(*args, **kwargs)

    def search(self):
        sqs = super().search()
        if self.category:
            query = None
            for category in self.category:
                if query:
                    query += u' OR '
                else:
                    query = u''
                query += u'"%s"' % sqs.query.clean(category)
            sqs = sqs.narrow(u'category_exact:%s' % query)
        if self.location:
            query = None
            for location in self.location:
                if query:
                    query += u' OR '
                else:
                    query = u''
                query += u'"%s"' % sqs.query.clean(location)
            sqs = sqs.narrow(u'location_exact:%s' % query)
        return sqs
