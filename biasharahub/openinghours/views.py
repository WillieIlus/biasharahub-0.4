from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404

from business.models import Business
from openinghours.forms import OpeningHoursFormset, OpeningHoursFormsetHelper
from openinghours.models import OpeningHours


@login_required
def opening_hours(request, slug):
    """company = get_object_or_404(Business, slug=slug)"""
    instance = Business.objects.get(slug=slug)
    formset = OpeningHoursFormset(request.POST or None, request.FILES or None, instance=instance,
                                  initial=[{'weekday': x} for x in range(1, 8)]
                                  )
    formset.company = instance

    helper = OpeningHoursFormsetHelper()

    if formset.is_valid():
        formset.save()
        messages.success(request, "Successfully Created")
        return HttpResponseRedirect(instance.get_absolute_url())

    context = {
        "helper": helper,
        "formset": formset,
    }
    return render(request, "openinghours/formset.html", context)


@login_required
def opening_hours_edit(request, slug,):
    instance = get_object_or_404(Business, slug=slug)
    # instances = get_object_or_404(OpeningHours, id=id)
    # instance = Business.objects.get(slug=slug)
    formset = OpeningHoursFormset(request.POST or None, request.FILES or None, instance=instance,
                                  initial=[{'weekday': x} for x in range(1, 8)]
                                  )
    # formset.company = instance

    helper = OpeningHoursFormsetHelper()

    if formset.is_valid():
        formset.save()
        messages.success(request, "Successfully Created")
        return HttpResponseRedirect(instance.get_absolute_url())

    context = {
        "helper": helper,
        "formset": formset,
    }
    return render(request, "openinghours/formset.html", context)
