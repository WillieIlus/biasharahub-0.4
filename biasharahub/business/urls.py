from django.urls import path

from favourites.views import bookmark_company
from .views import BusinessCreate, BusinessDetail, BusinessList, BusinessEdit, add_photos, PhotoGallery, \
    FacetedSearchView, autocomplete

app_name = 'business'

urlpatterns = [
    path('new/', BusinessCreate.as_view(), name='new'),
    path('list/', BusinessList.as_view(), name='list'),

    path('', FacetedSearchView.as_view(), name='search'),

    path('<slug:slug>/', BusinessDetail.as_view(), name='detail'),
    path('<slug:slug>/edit/', BusinessEdit.as_view(), name='edit'),
    path('<slug:slug>/add_photos/', add_photos, name='photos'),
    path('<slug:slug>/gallery/', PhotoGallery.as_view(), name='gallery'),
    path('<slug:slug>/bookmark/', bookmark_company, name='bookmark'),
    path('autocomplete/', autocomplete),

]
