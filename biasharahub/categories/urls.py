from django.urls import path

from .views import CategoryCreate, CategoryDetail, CategoryList, CategoryUpdate

app_name = 'categories'

urlpatterns = [
    path('new/', CategoryCreate.as_view(), name='new'),
    path('<slug:slug>/', CategoryDetail.as_view(), name='detail'),
    path('<slug:slug>/edit/', CategoryUpdate.as_view(), name='edit'),

    path('', CategoryList.as_view(), name='list'),

]
