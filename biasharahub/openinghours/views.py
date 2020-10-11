from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.forms import inlineformset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import render
from extra_views import UpdateWithInlinesView, InlineFormSetFactory

from business.models import Business
from openinghours.forms import OpeningHoursForm
from openinghours.models import OpeningHours

openinghoursformset = inlineformset_factory(Business, OpeningHours, OpeningHoursForm, min_num=7, max_num=7,
                                            can_delete=False, can_order=False)


class OpeningHoursInline(InlineFormSetFactory):
    model = OpeningHours
    form_class = OpeningHoursForm


class OpeningHoursUpdateView(UpdateWithInlinesView):
    model = Business
    inlines = [OpeningHoursInline]
    fields = ['name']
    template_name = 'openinghours/updateformset.html'


@login_required
def opening_hours(request, slug):
    company = Business.objects.get(slug=slug)

    openinghoursformset = inlineformset_factory(Business, OpeningHours, OpeningHoursForm, min_num=7, max_num=7,
                                                can_delete=False, can_order=False)

    if request.method == "POST":
        formset = openinghoursformset(
            # request.POST, request.FILES,
            instance=company, initial=[{'weekday': x} for x in range(1, 8)])
        if formset.is_valid():
            formset.save()
            messages.success(request, "Successfully Created")
            return HttpResponseRedirect(company.get_absolute_url())
    else:
        formset = openinghoursformset(instance=company,
                                      initial=[{'weekday': x} for x in range(1, 8)]
                                      )

    context = {
        "formset": formset,
    }
    return render(request, "openinghours/formset.html", context)
