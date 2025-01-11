import plotly.graph_objects as go
from django.shortcuts import render, redirect
import json
from django.conf import settings
import os

def load_questions():
    with open(os.path.join(settings.BASE_DIR, 'questions.json'), 'r') as file:
        questions = json.load(file)
    return questions

def load_suggestions():
    with open(os.path.join(settings.BASE_DIR, 'suggestions.json'), 'r') as file:
        suggestions = json.load(file)
    return suggestions

def survey_view(request):
    questions = load_questions()
    total_questions = len(questions)
    question_index = int(request.GET.get('q', 0))

    if question_index >= total_questions:
        return redirect('results')

    if request.method == 'POST':
        selected_option = request.POST.get('option')
        question_id = int(request.POST.get('question_id'))

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
    suggestions = load_suggestions()
    question_dict = {q['id']: q for q in questions}

    category_scores = {}
    category_max_scores = {}
    category_percentages = {}
    category_details = {}

    for question_id, selected_option in answers.items():
        question = question_dict[int(question_id)]
        category = question['category']
        selected_option_points = next((option['points'] for option in question['options'] if option['text'] == selected_option), 0)
        max_option_points = max(option['points'] for option in question['options'])

        if category not in category_scores:
            category_scores[category] = 0
            category_max_scores[category] = 0
        category_scores[category] += selected_option_points
        category_max_scores[category] += max_option_points

    for category, score in category_scores.items():
        max_score = category_max_scores[category]
        percentage = (score / max_score) * 100 if max_score > 0 else 0
        category_percentages[category] = percentage

        # Determine suggestions based on percentages
        for range_str, details in suggestions[category].items():
            range_start, range_end = map(int, range_str.split('-'))
            if range_start <= percentage <= range_end:
                category_details[category] = {
                    'title': details['title'],
                    'description': details['description'],
                    'tips': details['tips'],
                    'percentage': percentage
                }
                break

    labels = list(category_scores.keys())
    values = list(category_percentages.values())

    # Create a bar chart using Plotly
    fig = go.Figure(data=[go.Bar(x=labels, y=values, text=[f'{v:.2f}%' for v in values], textposition='auto')])

    fig.update_layout(
        title='Assessment Results',
        xaxis_title='Category',
        yaxis_title='Percentage',
        yaxis=dict(range=[0, 100]),  # Percentage range is always between 0 and 100
    )

    chart_html = fig.to_html(full_html=False)

    # Pass category details and percentages to the template
    context = {
        'chart_html': chart_html,
        'category_details': category_details
    }
    return render(request, 'survey/results.html', context)