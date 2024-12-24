from django.urls import path
from . import views

urlpatterns = [
    path('', views.survey_view, name='survey'),  # Survey form view
    path('results/', views.results_view, name='results'),  # Results view
]
