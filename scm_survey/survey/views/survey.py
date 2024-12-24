from django.shortcuts import render, redirect
from ..models import SurveyQuestion, SurveyResponse

def survey_view(request):
    questions = SurveyQuestion.objects.all()
    if request.method == 'POST':
        for question in questions:
            selected_option = request.POST.get(str(question.id))
            if selected_option:
                SurveyResponse.objects.create(
                    question=question,
                    response_text=selected_option,
                    selected=True
                )
        return redirect('results')
    return render(request, 'survey/survey.html', {'questions': questions})
