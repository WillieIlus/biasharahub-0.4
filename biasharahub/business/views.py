from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.http import request
from django.shortcuts import render, get_object_or_404
from django.utils.encoding import uri_to_iri
from django.views.generic import CreateView, ListView, UpdateView
from django.views.generic.detail import SingleObjectMixin, DetailView
from haystack.generic_views import FacetedSearchView as BaseFacetedSearchView
from haystack.query import SearchQuerySet

from business.models import Business, BusinessImage
from comments.forms import CommentForm
from reviews.forms import ReviewForm
from .forms import BusinessForm, BusinessPhotoFormSet, BusinessPhotoFormSetHelper, BusinessSearchForm


def autocomplete(request):
    sqs = SearchQuerySet().autocomplete(
        content_auto=request.GET.get(
            'query',
            ''))[
          :5]
    s = []
    for result in sqs:
        d = {"value": result.name, "data": result.object.slug}
        s.append(d)
    output = {'suggestions': s}
    return JsonResponse(output)


class FacetedSearchView(BaseFacetedSearchView):
    form_class = BusinessSearchForm
    facet_fields = ['category', 'location']
    template_name = 'business/search_result.html'
    paginate_by = 10
    context_object_name = 'object_list'


class BusinessList(ListView):
    model = Business
    paginate_by = 10
    context_object_name = "business"
    template_name = 'business/list.html'


class BusinessCreate(LoginRequiredMixin, CreateView):
    model = Business
    form_class = BusinessForm
    template_name = 'business/form.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.save()
        current_site = get_current_site(request)
        subject = '%s added to %s ' % (form.instance.name, current_site.name)
        message = 'Welcome to %s, %s was added ' \
                  'successfully, you can claim it here %s' % (
                      current_site.name, form.instance.name, form.instance.get_url)
        sender = form.instance.user.email
        recipients = form.instance.email
        send_mail(subject, message, sender, [recipients])
        return super().form_valid(form)


@login_required
def add_photos(request, slug):
    """company = get_object_or_404(Business, slug=slug)"""
    company = Business.objects.get(slug=slug)
    form = BusinessPhotoFormSet(request.POST or None, request.FILES or None, instance=company)
    helper = BusinessPhotoFormSetHelper()

    if form.is_valid():
        company = form.cleaned_data['company']
        img = form.cleaned_data['img']
        alt = form.cleaned_data['alt']
        gallery = BusinessImage(img=img, company=company, alt=alt)
        # form.save()
        gallery.save()
        messages.success(request, "Successfully Created")
        return HttpResponseRedirect(company.get_absolute_url())
    # else:
    #     return messages.error(request, 'There\'s and error in this form')
    context = {
        "helper": helper,
        "form": form,
    }
    return render(request, "business/formset.html", context)


class BusinessEdit(LoginRequiredMixin, UpdateView):
    model = Business
    slug_url_kwarg = 'slug'
    form_class = BusinessForm
    template_name = 'business/form.html'


class BusinessDetail(SingleObjectMixin, ListView):
    model = Business
    template_name = 'business/detail.html'
    context_object_name = 'business'
    slug_field = 'slug'
    paginate_by = 10
    count_hit = True

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=Business.objects.all())
        return super().get(request, *args, **kwargs)

    def get_object(self, **kwargs):
        slug = self.kwargs.get('slug')
        return get_object_or_404(Business, slug=uri_to_iri(slug))

    def get_queryset(self):
        return self.object.reviews.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ReviewForm()
        context['comment_form'] = CommentForm()
        # context['related_business'] = self.object.services.similar_objects()[:4]

        return context


class PhotoGallery(DetailView):
    model = Business
    template_name = 'business/photo_gallery.html'
    context_object_name = 'photo'
