from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def my_tracker(request):
    return HttpResponse("Welcome to Study Tracker!")