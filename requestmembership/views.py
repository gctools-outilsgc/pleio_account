from django.shortcuts import render

def requestmembership_step_one(request):
    return render(request, 'requestmembership_step_one.html')

def requestmembership_step_two(request):
    return render(request, 'requestmembership_step_two.html')

def requestmembership_complete(request):
    return render(request, 'requestmembership_complete.html')
