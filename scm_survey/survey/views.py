import plotly.graph_objects as go
from django.shortcuts import render, redirect
from django.urls import reverse
import json
import os
from django.conf import settings
from collections import defaultdict


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
    """Display the results of the survey with a radar chart."""
    # Retrieve the user's answers from the session
    answers = request.session.get('answers', {})
    if not answers:
        return render(request, 'survey/results.html', {
            'chart_html': None,
            'error': 'No answers found. Please complete the survey first.'
        })

    # Load all questions and create a lookup dictionary
    questions = load_questions()
    question_dict = {q['id']: q for q in questions}

    # Initialize a dictionary to accumulate category scores
    category_scores = defaultdict(int)

    # Process each answer to calculate category scores
    for question_id, selected_option_text in answers.items():
        try:
            question_id = int(question_id)  # Convert question ID to integer
        except ValueError:
            continue  # Skip invalid question IDs

        question = question_dict.get(question_id)
        if question:
            category = question['category']
            # Get the points for the selected option
            selected_option_points = next(
                (option['points'] for option in question['options'] if option['text'] == selected_option_text),
                0  # Default to 0 if the option is not found
            )
            category_scores[category] += selected_option_points

    # Prepare data for the radar chart
    labels = list(category_scores.keys())
    values = list(category_scores.values())

    # Ensure the radar chart forms a closed polygon
    if len(labels) > 2:
        labels.append(labels[0])  # Repeat the first label
        values.append(values[0])  # Repeat the first value

    # Create the radar chart using Plotly
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=labels,
        fill='toself',
        name='Assessment Results',
        line=dict(color="red", width=2)
    ))

    # Customize the chart layout
    fig.update_layout(
        polar=dict(
            bgcolor="#EAF6FF",
            radialaxis=dict(
                visible=True,
                range=[0, max(values) + 5],  # Adjust range dynamically
                showline=True,
                linewidth=2,
                linecolor="green",
                gridcolor="lightgray"
            ),
            angularaxis=dict(
                linewidth=2,
                linecolor="darkgray"
            ),
        ),
        title="Supply Chain Performance Radar",
        title_x=0.5,
        font=dict(size=16),
        paper_bgcolor="lightblue"
    )

    # Generate HTML for the chart
    chart_html = fig.to_html(full_html=False)

    # Render the results page
    return render(request, 'survey/results.html', {
        'chart_html': chart_html
    })
