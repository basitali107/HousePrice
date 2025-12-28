from django.shortcuts import render, redirect
from .forms import UserProfileForm



def landing_page(request):
    # Check if user is logged in
    if not request.session.get('user_id'):  # assuming you store user ID in session
        return redirect('login')  # redirect to login page if session not set
    
    # If session exists, show landing page
    return render(request, 'login.html')

def register(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            # You can hash password for security
            from django.contrib.auth.hashers import make_password
            user.password = make_password(form.cleaned_data['password'])
            user.save()
            return redirect('success')  # redirect to a success page
    else:
        form = UserProfileForm()
    
    return render(request, 'register.html', {'form': form})
