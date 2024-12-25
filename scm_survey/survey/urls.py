from django.urls import path
from django.contrib import admin
from .views import survey_view, results_view
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls), 
    path('survey/', survey_view, name='survey'), 
    path('results/', results_view, name='results'),
    path('', lambda request: redirect('/survey/')),
]
