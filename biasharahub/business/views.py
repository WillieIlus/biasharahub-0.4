from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import inlineformset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.utils.encoding import uri_to_iri
from django.views.generic import CreateView, ListView, UpdateView
from django.views.generic.detail import SingleObjectMixin, DetailView
from extra_views import UpdateWithInlinesView, InlineFormSetFactory
from haystack.generic_views import FacetedSearchView as BaseFacetedSearchView
from haystack.query import SearchQuerySet

from accounts.decorators import UserRequiredMixin
from business.models import Business, BusinessImage
from comments.forms import CommentForm
from reviews.forms import ReviewForm
from .forms import BusinessForm, BusinessSearchForm, \
    SocialProfileFormSet, BusinessPhotoForm


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
    paginate_by = 10
    context_object_name = "business"
    template_name = 'business/list.html'

    def get_queryset(self):
        return Business.objects.order_by('-publish')


class BusinessCreate(LoginRequiredMixin, CreateView):
    model = Business
    form_class = BusinessForm
    template_name = 'business/form.html'

    # object = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['social_form'] = SocialProfileFormSet(self.request.POST)

        else:
            context['social_form'] = SocialProfileFormSet()

        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.save()

        context = self.get_context_data(form=form)
        social_form = context['social_form']

        if social_form.is_valid():
            response = super().form_valid(form)
            social_form.instance = self.object
            social_form.save()
            return response
        else:
            return super().form_invalid(form)


@login_required
def add_photos(request, slug):
    business = Business.objects.get(slug=slug)
    BusinessPhotoFormSet = inlineformset_factory(Business, BusinessImage, form=BusinessPhotoForm, extra=6, max_num=12,
                                                 can_delete=True)
    if request.method == "POST":
        formset = BusinessPhotoFormSet(request.POST, request.FILES, instance=business,
                                       queryset=BusinessImage.objects.all)
        if formset.is_valid():
            # response = super().form_valid(form)
            formset.business = business
            formset.save()
            return HttpResponseRedirect(business.get_absolute_url())
    else:
        formset = BusinessPhotoFormSet(instance=business)
    return render(request, 'business/formset.html', {'formset': formset})


class PhotoInline(InlineFormSetFactory):
    model = BusinessImage
    form_class = BusinessPhotoForm


class PhotoUpdateView(UpdateWithInlinesView):
    model = Business
    inlines = [PhotoInline]
    fields = ['name']
    template_name = 'business/updateformset.html'


class BusinessEdit(LoginRequiredMixin, UserRequiredMixin, UpdateView):
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
