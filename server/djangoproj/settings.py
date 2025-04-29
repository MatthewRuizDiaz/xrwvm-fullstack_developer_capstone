# views.py
# from django.shortcuts import render # F401: Unused import render
# from django.http import HttpResponseRedirect, HttpResponse # F401
from django.contrib.auth.models import User
# from django.shortcuts import get_object_or_404, render, redirect # F401
from django.contrib.auth import logout
# from django.contrib import messages # F401: Unused import messages
# from datetime import datetime # F401: Unused import datetime
from .restapis import get_request, analyze_review_sentiments, post_review
from django.http import JsonResponse
from django.contrib.auth import login, authenticate
import logging
import json
from django.views.decorators.csrf import csrf_exempt
from .populate import initiate
from .models import CarMake, CarModel

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.

# Create a `login_request` view to handle sign in request
@csrf_exempt
def login_user(request):
    # Get username and password from request.POST dictionary
    data = json.loads(request.body)
    username = data.get('userName')  # Use .get for safety
    password = data.get('password')
    if not username or not password:
        return JsonResponse({"error": "Missing username or password"}, status=400)

    # Try to check if provided credential can be authenticated
    user = authenticate(username=username, password=password)
    response_data = {"userName": username}
    if user is not None:
        # If user is valid, call login method to login current user
        login(request, user)
        response_data = {"userName": username, "status": "Authenticated"}
        return JsonResponse(response_data)
    else:
        return JsonResponse({"userName": username, "status": "Authentication Failed"}, status=401)


# Create a `logout_request` view to handle sign out request
def logout_request(request):
    logout(request)
    data = {"userName": ""}
    return JsonResponse(data)


# Create a `registration` view to handle sign up request
@csrf_exempt
def registration(request):
    try:
        data = json.loads(request.body)
        username = data.get('userName')
        password = data.get('password')
        first_name = data.get('firstName')
        last_name = data.get('lastName')
        email = data.get('email')

        # Basic validation
        if not all([username, password, first_name, last_name, email]):
            return JsonResponse({"error": "Missing required fields"}, status=400)

        if User.objects.filter(username=username).exists():
            return JsonResponse(
                {'userName': username, 'error': 'Already Registered'}, status=409
            )
        if User.objects.filter(email=email).exists():
            return JsonResponse(
                {'email': email, 'error': 'Email already in use'}, status=409
            )

        # Create new user
        new_user = User.objects.create_user(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            email=email
        )
        # Log in the new user
        login(request, new_user)
        response_data = {"userName": username, "status": "Authenticated"}
        return JsonResponse(response_data)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return JsonResponse({"error": "Registration failed"}, status=500)


def get_cars(request):
    count = CarMake.objects.count()
    print(count)
    if count == 0:
        initiate()

    car_models = CarModel.objects.select_related('car_make')
    cars = []
    for car_model in car_models:
        cars.append(
            {"CarModel": car_model.name, "CarMake": car_model.car_make.name}
        )
    return JsonResponse({"CarModels": cars})


# Update the `get_dealerships` view to render list of dealerships
# all by default, particular state if state is passed
def get_dealerships(request, state="All"):
    if state == "All":
        endpoint = "/fetchDealers"
    else:
        endpoint = f"/fetchDealers/{state}"  # Use f-string

    dealerships = get_request(endpoint)
    if dealerships is not None:
        return JsonResponse({"status": 200, "dealers": dealerships})
    else:
        # Handle case where get_request failed
        return JsonResponse({"status": 500, "message": "Failed to fetch dealerships"})


# Create a `get_dealer_reviews` view to render the reviews of a dealer
def get_dealer_reviews(request, dealer_id):
    # if dealer id has been provided
    if dealer_id:
        endpoint = f"/fetchReviews/dealer/{dealer_id}"
        reviews = get_request(endpoint)
        if reviews is not None:
            for review_detail in reviews:
                try:
                    # Pass review text to sentiment analyzer
                    sentiment_response = analyze_review_sentiments(
                        review_detail.get('review', '')  # Use .get for safety
                    )
                    # Assign sentiment if analysis was successful
                    if sentiment_response and 'sentiment' in sentiment_response:
                        review_detail['sentiment'] = sentiment_response['sentiment'].get('label', 'unknown')
                    else:
                        review_detail['sentiment'] = 'analysis_failed'
                except Exception as e:
                    logger.error(f"Error analyzing sentiment: {e}")
                    review_detail['sentiment'] = 'error'

            return JsonResponse({"status": 200, "reviews": reviews})
        else:
            return JsonResponse({"status": 404, "message": "Reviews not found or error fetching"})
    else:
        return JsonResponse({"status": 400, "message": "Bad Request: Missing dealer_id"})


# Create a `get_dealer_details` view to render the dealer details
def get_dealer_details(request, dealer_id):
    if dealer_id:
        endpoint = f"/fetchDealer/{dealer_id}"
        dealership = get_request(endpoint)
        if dealership is not None:
            # Assuming the response structure might be nested like {'dealer': {...}}
            # Adjust based on actual API response
            if isinstance(dealership, list) and len(dealership) > 0:
                actual_dealer_data = dealership[0]  # Take first if it's a list
            else:
                actual_dealer_data = dealership  # Assume it's the dict directly

            return JsonResponse({"status": 200, "dealer": actual_dealer_data})
        else:
            return JsonResponse({"status": 404, "message": "Dealer not found or error fetching"})