from django.urls import path

from openinghours.views import opening_hours, opening_hours_edit  # , OpeningHoursCreate, OpeningHoursEdit

app_name = 'openinghours'

urlpatterns = [
    path('<slug:slug>/update/', opening_hours_edit, name='edit_open_hours'),
    path('<slug:slug>/opening_hours/', opening_hours, name='open_hours'),

    # path('<slug:slug>/open/', OpeningHoursCreate.as_view(), name='add_open_hours'),
    # path('<pk>/edit/', OpeningHoursEdit.as_view(), name='edit_open_hours'),

]
