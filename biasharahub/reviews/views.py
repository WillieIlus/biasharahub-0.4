import warnings

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.generic import ListView, CreateView, UpdateView
from django.views.generic.detail import SingleObjectMixin
from hitcount.models import HitCount
from hitcount.utils import RemovedInHitCount13Warning
from hitcount.views import HitCountMixin

from business.models import Business
from comments.forms import CommentForm
from reviews.forms import ReviewForm, ReviewPhotoFormSetHelper, ReviewPhotoFormSet
from .models import Review


class ReviewCreate(LoginRequiredMixin, CreateView):
    model = Review
    form_class = ReviewForm
    template_name = 'includes/form.html'

    def form_valid(self, form):
        form.instance.content_object = get_object_or_404(Business, slug=self.kwargs['slug'])
        form.instance.user = self.request.user
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.warning(self.request, 'There was an error in this form')
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse('business:detail', kwargs={'slug': self.object.content_object.slug})


@login_required
def photos(request, slug):
    """company = get_object_or_404(Business, slug=slug)"""
    review = Review.objects.get(slug=slug)
    form = ReviewPhotoFormSet(request.POST or None, request.FILES or None, instance=review)
    helper = ReviewPhotoFormSetHelper()

    if form.is_valid():
        form.save()
        messages.success(request, "Successfully Created")
    context = {
        "helper": helper,
        "form": form,
    }
    return render(request, "business/formset.html", context)


class ReviewEdit(LoginRequiredMixin, UpdateView):
    model = Review
    form_class = ReviewForm
    template_name = 'includes/form.html'


class ReviewList(ListView):
    model = Review
    context_object_name = 'review'
    template_name = 'reviews/list.html'
    paginate_by = 10


class ReviewDetail(SingleObjectMixin, HitCountMixin, ListView):
    model = Review
    paginate_by = 10
    context_object_name = 'review'
    template_name = 'reviews/detail.html'
    count_hit = True

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=Review.objects.all())
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        # context.update({'popular_reviews': Review.objects.order_by('-hit_count_generic__hits')[:3], })

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

    def get_queryset(self):
        return self.object.comments.all()


class UserReviews(ListView):
    context_object_name = 'review'
    template_name = 'reviews/user_reviews.html'

    def get_queryset(self):
        user = self.request.user
        return Review.objects.filter(user=user).order_by('-publish')
