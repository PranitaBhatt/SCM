from django.shortcuts import render, redirect
from django.db.models import Count
from .models import SurveyQuestion, SurveyResponse

def survey_view(request):
    if request.method == 'POST':
        responses = []
        for key in request.POST:
            if key.startswith('option_'):
                responses.append(request.POST[key])
        # Save responses logic here
        return redirect('results')
    return render(request, 'survey/survey.html')


def results_view(request):
            selected_options=[]
            chart_data = [0, 0, 0, 0, 0]  # Default data values
            if request.method == "POST":
             selected_options = [
            "Maximizing company Sales" if request.POST.get("option_1") else "",
            "Maximizing company profits" if request.POST.get("option_2") else "",
            "Minimizing operational costs" if request.POST.get("option_3") else "",
            "Minimizing inventory costs" if request.POST.get("option_4") else "",
            "Ensuring the best service for customers" if request.POST.get("option_5") else "",
            "Logistics & Distribution" if request.POST.get("area_1") else "",
            "Inventory Management" if request.POST.get("area_2") else "",
            "Demand Forecasting" if request.POST.get("area_3") else "",
            "SCM Analytics" if request.POST.get("area_4") else "",
            "Excel & Data Management" if request.POST.get("area_5") else "",
        ]
             selected_options = list(filter(None, selected_options))
            
             if "Logistics & Distribution" in selected_options:
                   chart_data[0] = 85
             if "Inventory Management" in selected_options:
                  chart_data[1] = 95
            if "Demand Forecasting" in selected_options:
                 chart_data[2] = 60
            if "SCM Analytics" in selected_options:
                 chart_data[3] = 100
            if "Excel & Data Management" in selected_options:
                chart_data[4] = 90
            data = {
        "labels": ['Logistics & Distribution', 'Inventory Management', 'Demand Forecasting', 'SCM Analytics', 'Excel & Data'],
        "values": chart_data,  # Dynamically generated values based on selected options
            }
            print(chart_data)
            return render(request, 'survey/results.html', {'data': data, 'selected_options': selected_options})