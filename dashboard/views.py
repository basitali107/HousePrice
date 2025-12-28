from django.shortcuts import render, redirect
from accounts.models import UserProfile

def dashboard(request):
    if not request.session.get('user_id'):
        return redirect('login')

    total_users = UserProfile.objects.count()

    context = {
        'total_users': total_users,
        'total_houses': 0,
        'total_predictions': 0,
        'avg_price': 0,
    }

    return render(request, 'dashboard/dashboard.html')
