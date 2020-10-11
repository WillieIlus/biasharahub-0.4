from django.urls import path

from openinghours.views import opening_hours, OpeningHoursUpdateView

app_name = 'openinghours'

urlpatterns = [
    path('<slug:slug>/opening_hours/', opening_hours, name='update'),
    path('<slug:slug>/update/', OpeningHoursUpdateView.as_view(), name='opening_hours_update'),
]
