from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views.generic.detail import SingleObjectMixin

from categories.forms import CategoryForm
from categories.models import Category


class CategoryList(ListView):
    model = Category
    paginate_by = 12
    context_object_name = "category"
    template_name = 'categories/list.html'


class CategoryDetail(SingleObjectMixin, ListView):
    model = Category
    context_object_name = "category"
    template_name = 'categories/detail.html'
    paginate_by = 15

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=Category.objects.all())
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return self.object.company.all()


class CategoryCreate(LoginRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'includes/form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = " Add Category "
        return context


class CategoryUpdate(LoginRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'includes/form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = " Update Category "
        return context
