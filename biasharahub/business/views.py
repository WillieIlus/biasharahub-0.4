import warnings

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.http import request
from django.shortcuts import render
from django.views.generic import CreateView, ListView, UpdateView
from django.views.generic.detail import SingleObjectMixin, DetailView
from haystack.generic_views import FacetedSearchView as BaseFacetedSearchView
from haystack.query import SearchQuerySet
from hitcount.models import HitCount
from hitcount.utils import RemovedInHitCount13Warning
from hitcount.views import HitCountMixin

from business.models import Business, BusinessImage
from comments.forms import CommentForm
from reviews.forms import ReviewForm
from .forms import BusinessForm, BusinessPhotoFormSet, BusinessPhotoFormSetHelper, ClaimBusinessForm, BusinessSearchForm


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

    # if not company.owner:
    #     if company.user != request.user or request.user.is_superuser:
    #         raise PermissionDenied
    # elif company.owner != request.user or request.user.is_superuser:
    #     raise PermissionDenied

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


class ClaimBusiness(LoginRequiredMixin, UpdateView):
    model = Business
    slug_url_kwarg = 'slug'
    form_class = ClaimBusinessForm
    template_name = 'business/form.html'

    # def get_object(self, *args, **kwargs):
    #     obj = super().get_object(*args, **kwargs)
    #     if not obj.owner:
    #         if not obj.user == self.request.user and not self.request.user.is_superuser:
    #             raise PermissionDenied
    #     elif not obj.owner == self.request.user and not self.request.user.is_superuser:
    #         raise PermissionDenied
    #     else:
    #         return obj


class BusinessEdit(LoginRequiredMixin, UpdateView):
    model = Business
    slug_url_kwarg = 'slug'
    form_class = BusinessForm
    template_name = 'business/form.html'

    # def dispatch(self, request, *args, **kwargs):
    #     obj = super().get_object()
    #     if obj.owner is None:
    #         if obj.user != self.request.user or self.request.user.is_superuser:
    #             raise PermissionDenied
    #     elif obj.owner != self.request.user or self.request.user.is_superuser:
    #         raise PermissionDenied
    #     else:
    #         return obj
    #     return super().dispatch(request, *args, **kwargs)


class BusinessDetail(SingleObjectMixin, HitCountMixin, ListView):
    model = Business
    template_name = 'business/detail.html'
    context_object_name = 'business'
    slug_field = 'slug'
    paginate_by = 10
    count_hit = True

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=Business.objects.all())
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return self.object.reviews.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ReviewForm()
        context['comment_form'] = CommentForm()
        # context['related_business'] = self.object.services.similar_objects()[:4]

        if self.object:
            hit_count = HitCount.objects.get_for_object(self.object)
            hits = hit_count.hits
            context['hitcount'] = {'pk': hit_count.pk}

            if self.count_hit:
                hit_count_response = self.hit_count(self.request, hit_count)
                if hit_count_response.hit_counted:
                    hits = hits + 1
                context['hitcount']['hit_counted'] = hit_count_response.hit_counted
                context['hitcount']['hit_message'] = hit_count_response.hit_message

            context['hitcount']['total_hits'] = hits

        return context

    def _update_hit_count(request, hitcount):
        """
        Deprecated in 1.2. Use hitcount.views.Hit CountMixin.hit_count() instead.
        """
        warnings.warn(
            "hitcount.views._update_hit_count is deprecated. "
            "Use hitcount.views.HitCountMixin.hit_count() instead.",
            RemovedInHitCount13Warning
        )
        return HitCountMixin.hit_count(request, hitcount)


class PhotoGallery(DetailView):
    model = Business
    template_name = 'business/photo_gallery.html'
    context_object_name = 'photo'
