from django.shortcuts import render
from django.db.models import Count
from ..models import SurveyResponse

def results_view(request):
    results = SurveyResponse.objects.values('question__question_text').annotate(
        total=Count('id')
    )
    data = {
        'labels': [res['question__question_text'] for res in results],
        'values': [res['total'] for res in results],
    }
    return render(request, 'survey/results.html', {'data': data})
