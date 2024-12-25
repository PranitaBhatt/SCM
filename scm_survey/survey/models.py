from django.db import models

class SurveyQuestion(models.Model):
    question_text = models.CharField(max_length=200)
    options = models.JSONField() # Store options as a JSON array 
    category = models.CharField(max_length=100)

    def __str__(self):
        return self.question_text

class SurveyResponse(models.Model):
    question = models.ForeignKey(SurveyQuestion, on_delete=models.CASCADE)
    response_text = models.CharField(max_length=200)
    selected = models.BooleanField(default=False)

    def __str__(self):
        return self.response_text
