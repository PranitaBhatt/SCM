import plotly.graph_objects as go
from django.shortcuts import render, redirect
import json
from django.conf import settings
import os

def load_questions():
    with open(os.path.join(settings.BASE_DIR, 'questions.json'), 'r') as file:
        questions = json.load(file)
    return questions

def survey_view(request):
    questions = load_questions()
    total_questions = len(questions)
    question_index = int(request.GET.get('q', 0))

    # Ensure question index is within valid range
    if question_index >= total_questions:
        return redirect('results')

    if request.method == 'POST':
        selected_option = request.POST.get('option')
        question_id = int(request.POST.get('question_id'))

        # Store the answer in the session
        if 'answers' not in request.session:
            request.session['answers'] = {}
        request.session['answers'][question_id] = selected_option

        question_index += 1
        if question_index < total_questions:
            return redirect(f'/survey/?q={question_index}')
        else:
            return redirect('results')

    current_question = questions[question_index]
    return render(request, 'survey/survey.html', {
        'question': current_question,
        'question_index': question_index + 1,
        'total_questions': total_questions
    })

def results_view(request):
    answers = request.session.get('answers', {})
    questions = load_questions()
    question_dict = {q['id']: q for q in questions}

    category_scores = {}

    for question_id, selected_option in answers.items():
        question = question_dict[int(question_id)]
        category = question['category']
        selected_option_points = next((option['points'] for option in question['options'] if option['text'] == selected_option), 0)
        
        if category not in category_scores:
            category_scores[category] = 0
        category_scores[category] += selected_option_points

    labels = list(category_scores.keys())
    values = list(category_scores.values())

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=labels,
        fill='toself',
        name='Assessment Results'
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, max(values)]
            )),
        showlegend=False
    )

    chart_html = fig.to_html(full_html=False)

    return render(request, 'survey/results.html', {'chart_html': chart_html})
