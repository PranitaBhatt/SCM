from django.contrib import admin
from .models import SurveyQuestion, SurveyResponse

admin.site.register(SurveyQuestion)
admin.site.register(SurveyResponse)
