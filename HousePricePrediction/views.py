import pandas as pd
import numpy as np
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error
import joblib
from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
from django.http import HttpResponse
from django.conf import settings
from sklearn.preprocessing import OneHotEncoder
import os
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from .models import UserProfile
from .models import UserProfile
from django.contrib.auth.hashers import make_password, check_password

from django.views.decorators.cache import never_cache  # ✅ THIS IMPORT IS REQUIRED



@csrf_protect


@never_cache
def home(request):
    if not request.session.get('user_id'):
        return redirect('login')

    response = render(request, 'home.html', {'user_name': request.session.get('user_name')})
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response



        







def predict(request):
    """Render the prediction form page"""
    return render(request, 'predict.html')



from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from .models import UserProfile

def register(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        profile_pic = request.FILES.get('profile_pic')  # Optional

        # Validation
        if not all([full_name, email, phone, address, password1, password2]):
            messages.error(request, "All fields are required")
            return render(request, 'register.html')

        if password1 != password2:
            messages.error(request, "Passwords do not match")
            return render(request, 'register.html')

        if UserProfile.objects.filter(email=email).exists():
            messages.error(request, "Email already exists")
            return render(request, 'register.html')

        # SAVE USER
        UserProfile.objects.create(
            full_name=full_name,
            email=email,
            phone=phone,
            address=address,
            profile_pic=profile_pic,
            password=make_password(password1)
        )

        messages.success(request, "Registration successful. Please login.")
        return redirect('login')

    # GET request
    return render(request, 'register.html')


# Login
def login_view(request):
    """Handle user login"""

    # ✅ If already logged in, go to home
    if request.session.get('user_id'):
        return redirect('home')

    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')

        if not email or not password:
            messages.error(request, 'Email and password are required')
            return render(request, 'login.html')

        try:
            user = UserProfile.objects.get(email=email)

            if check_password(password, user.password):
                # ✅ Set session
                request.session['user_id'] = user.id
                request.session['user_name'] = user.full_name
                request.session['user_email'] = user.email

                messages.success(request, f'Welcome back, {user.full_name}!')

                # ✅ Redirect to home (or next if exists)
                next_page = request.GET.get('next', 'home')
                return redirect(next_page)

            else:
                messages.error(request, 'Invalid email or password')

        except UserProfile.DoesNotExist:
            messages.error(request, 'Invalid email or password')

    return render(request, 'login.html')


# Logout
def logout_view(request):
    """Handle user logout"""
    user_name = request.session.get('user_name', 'User')
    request.session.flush()
    messages.success(request, f'Goodbye, {user_name}! You have been logged out.')
    return redirect('login')


#  home page
def  home_page(request):
    """ home/Home page"""
    if not request.session.get('user_id'):
        messages.warning(request, 'Please login to access the home page')
        return redirect('login')
    return render(request, 'home.html')

def price_page(request):
    context = {}  # You can pass any data here
    return render(request, 'accounts/price_page.html', context)



# Result page (example for predictions)
def result(request):
    """Display prediction results"""
    if not request.session.get('user_id'):
        messages.warning(request, 'Please login to view predictions')
        return redirect('login')

    context = {
        'user_name': request.session.get('user_name')
    }
    return render(request, 'result.html', context)







file_path = os.path.join(os.path.dirname(__file__), 'static', 'Housing.csv')
data = pd.read_csv(file_path)
data = pd.read_csv(file_path)
#data = data.drop(columns=['price'])
#data.head()

#print("Missing values before handling:")
#print(data.isnull().sum())
imputer = SimpleImputer(strategy="mean")

numeric_columns = data.select_dtypes(include=['number']).columns
non_numeric_columns = data.select_dtypes(exclude=['number']).columns


data[numeric_columns] = pd.DataFrame(
imputer.fit_transform(data[numeric_columns]),
columns=numeric_columns
)

#print("Missing values after handling:")
#print(data.isnull().sum())

data.columns = data.columns.str.strip().str.lower()  # Remove spaces and convert to lowercase

#print(data.columns)


X = ['bedrooms', 'bathrooms', 'stories', 'area', 'guestroom', 'parking']
columns_to_select = ['bedrooms', 'bathrooms', 'stories', 'area', 'guestroom', 'parking']
try:
        X = data[columns_to_select]
        #print("Columns selected successfully!")
except KeyError as e:
        print(f"Error selecting columns: {e}")
    #print(X.head())
y = data['price'] 
test_size = 0.2  # 80% for training and 20% for testing
random_state = 42

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state)

#print(X_train.isnull().sum())  # For features
#print(y_train.isnull().sum()) 

X_train = X_train.dropna()
y_train = y_train[X_train.index]

X_train = pd.get_dummies(X_train, drop_first=True)
X_test = pd.get_dummies(X_test, drop_first=True)

print(X_train.shape)
print(y_train.shape)

model = LinearRegression()
model.fit(X_train, y_train)
y_pred = model.predict(X_test)

joblib.dump(model, 'housing_model.pkl')
print("Model trained and saved successfully.")



def result(request):
    # Load the pre-trained model
    try:
        model = joblib.load('housing_model.pkl')
    except FileNotFoundError:
        return HttpResponse("Model not found. Please train the model first.", status=500)

    if request.method == 'POST':
        try:
            # Retrieving input values and ensuring they're converted to integers
            bedroom = int(request.POST.get('bedroom'))
            bathroom = int(request.POST.get('bathroom'))
            stories = int(request.POST.get('stories'))
            area = int(request.POST.get('area'))
        
            # Get guestroom and parking values as integers (1 or 0)
            guestroom = int(request.POST.get('guestroom'))  # Will be 1 or 0 based on the selection
            parking = int(request.POST.get('parking'))     # Will be 1 or 0 based on the selection

            
# New input data (ensure values for bedroom, bathroom, stories, area, guestroom, and parking are provided)
            new_data = pd.DataFrame({
                                        'bedrooms': [bedroom],
                                        'bathrooms': [bathroom],
                                        'stories': [stories],
                                        'area': [area],
                                        'guestroom_yes': [guestroom ],  # Correct ternary logic
                                        'parking_yes': [parking],    # Correct ternary logic
                                    })


            imputer = SimpleImputer(strategy="mean")
            new_data_imputed = pd.DataFrame(imputer.fit_transform(new_data), columns=new_data.columns)


            new_data_encoded = pd.get_dummies(new_data_imputed, drop_first=True)


            new_data_encoded = new_data_encoded.reindex(columns=X_train.columns, fill_value=0)
            # Find missing columns between new data and model's columns
            predicted_price = model.predict(new_data_encoded)

            
            rounded_predicted_price = round(predicted_price[0])
            readable_price = f"{rounded_predicted_price:,}"

            return render(request, 'pridct.html', {'predicted_price': readable_price })

        except Exception as e:
            return HttpResponse(f"Error during prediction: {e}", status=500)



    return HttpResponse("Invalid request method.", status=405)

def pridct(request):
    return render(request, 'pridct.html')