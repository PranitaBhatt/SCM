import plotly.graph_objects as go
from django.shortcuts import render, redirect
from django.urls import reverse
import json
import os
from django.conf import settings
from collections import defaultdict
import plotly.express as px

def load_questions():
    """Load questions from a JSON file."""
    try:
        with open(os.path.join(settings.BASE_DIR, 'questions.json'), 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        raise RuntimeError("Questions file not found. Ensure 'questions.json' exists.")
    except json.JSONDecodeError:
        raise RuntimeError("Invalid JSON format in 'questions.json'.")

def survey_view(request):
    """Handle the survey view where questions are displayed one at a time."""
    questions = load_questions()
    total_questions = len(questions)
    question_index = request.GET.get('q', 0)

    try:
        question_index = int(question_index)
    except ValueError:
        question_index = 0

    # If all questions have been answered, redirect to the results page
    if question_index >= total_questions:
        return redirect(reverse('results'))

    # Handle POST requests to save answers
    if request.method == 'POST':
        selected_option = request.POST.get('option')
        question_id = request.POST.get('question_id')

        try:
            question_id = int(question_id)
        except (ValueError, TypeError):
            return redirect(reverse('survey'))

        # Initialize session storage for answers if it doesn't exist
        if 'answers' not in request.session:
            request.session['answers'] = {}

        # Store the answer for the current question
        request.session['answers'][str(question_id)] = selected_option
        request.session.modified = True  # Mark session as modified to persist changes

        # Redirect to the next question
        question_index += 1
        return redirect(reverse('survey') + f'?q={question_index}')

    # Retrieve the current question based on the index
    current_question = questions[question_index]
    return render(request, 'survey/survey.html', {
        'question': current_question,
        'question_index': question_index + 1,
        'total_questions': total_questions
    })

def results_view(request):
    """Display the results of the survey with percentages in bar and line charts."""
    answers = request.session.get('answers', {})
    if not answers:
        return render(request, 'survey/results.html', {
            'chart_html': None,
            'error': 'No answers found. Please complete the survey first.'
        })

    questions = load_questions()
    question_dict = {q['id']: q for q in questions}

    category_scores = defaultdict(int)
    total_points = 0

    for question_id, selected_option_text in answers.items():
        try:
            question_id = int(question_id)
        except ValueError:
            continue

        question = question_dict.get(question_id)
        if question:
            category = question['category']
            selected_option_points = next(
                (option['points'] for option in question['options'] if option['text'] == selected_option_text), 0
            )
            category_scores[category] += selected_option_points
            total_points += selected_option_points

    # Convert raw scores to percentages
    category_percentages = {
        category: (score / total_points) * 100 for category, score in category_scores.items()
    }

    # Bar chart: Percentages by category
    bar_chart = px.bar(
        x=list(category_percentages.keys()),
        y=list(category_percentages.values()),
        labels={"x": "Category", "y": "Percentage (%)"},
        title="Survey Results by Category (in Percentage)",
        color_discrete_sequence=["#FF5A5F"]
    )
    bar_chart.update_layout(
        plot_bgcolor="white",
        xaxis=dict(title=dict(font=dict(size=12))),
        yaxis=dict(title=dict(font=dict(size=12)), gridcolor="lightgray"),
    )

    # Line chart (optional: if using time-series or other sequential data)
    line_chart = go.Figure()
    line_chart.add_trace(go.Scatter(
        x=list(category_percentages.keys()),
        y=list(category_percentages.values()),
        mode="lines+markers",
        line=dict(color="#FF5A5F", width=2),
        marker=dict(size=6),
        name="Category Percentage"
    ))
    line_chart.update_layout(
        title="Percentage Distribution Across Categories",
        plot_bgcolor="white",
        xaxis=dict(gridcolor="lightgray"),
        yaxis=dict(gridcolor="lightgray"),
    )

    # Combine both charts into the result
    chart_html = bar_chart.to_html(full_html=False) + line_chart.to_html(full_html=False)

    return render(request, 'survey/results.html', {
        'chart_html': chart_html
    })
