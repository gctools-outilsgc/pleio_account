from django.shortcuts import render, HttpResponseRedirect
from .forms import RequestStepOne, RequestStepTwo

def requestmembership_step_one(request):
    if request.method == 'POST':
        form = RequestStepOne(request.POST)
    else:
        form = RequestStepOne()

    if 'step_one_form' in request.session:
        data = request.session['step_one_form']
        
        for attr, value in data.items():
            form.fields[attr].initial = value

        del request.session['step_one_form']

    return render(request, 'requestmembership_step_one.html', {'form': form})

def requestmembership_step_two(request):
    if request.method == 'POST':
        form = RequestStepOne(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            form2 = RequestStepTwo()
            request.session['step_one_form'] = data;
            return render(request, 'requestmembership_step_two.html', {'form': form2, 'data': data})
        else:
            return render(request, 'requestmembership_step_one.html', {'form': form})
    else:
        return HttpResponseRedirect('/request/one/')

    def clean(self):
        if 'back' in self.data:
            form = RequestStepOne(request.POST)
            return render(request, 'requestmembership_step_one.html', {'form': form})

def requestmembership_complete(request):
    return render(request, 'requestmembership_complete.html')
