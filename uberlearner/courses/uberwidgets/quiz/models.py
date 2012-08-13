from django.db import models
from courses.uberwidgets.models import UberWidget
from django.contrib.auth.models import User

"""
General comments on the current state of the quiz app.
======================================================
The app stores the overall results of a quiz but doesn't store
the results of each question. A proper modelling of this widget
needs to be done. The current model is a cursory and unplanned
version.

In the final version, categories should be assigned to each quiz
and to each question. Then based on the correctness of the answers
for each type of question, a general profile of the test-taker's 
abilities can be assessed. These categories could be of types 
"analytical", "subjective" etc. The student could then be given 
feedback on the types of skills they possess and the courses they 
should take (recommendations) that will enhance the ones they 
don't yet possess.

And obviously, the results of each test-taker for each of the 
questions of each attempt of each quiz will have to be stored.
"""

class Result(models.Model):
    timestamp = models.DateTimeField()
    score = models.PositiveIntegerField()
    quiz = models.ForeignKey('Quiz')
    user = models.ForeignKey(User)

class Quiz(UberWidget):
    title = models.CharField(max_length=75)
    user = models.ManyToManyField(through=Result)
    
class Question(models.Model):
    text = models.TextField()
    quiz = models.ForeignKey(Quiz)
    correct_answer = models.ForeignKey('Answer')
    
    class Meta:
        order_with_respect_to = 'quiz'
    
class Answer(models.Model):
    text = models.TextField()
    question = models.ForeignKey
    
    class Meta:
        order_with_respect_to = 'question'