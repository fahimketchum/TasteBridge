import json

from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect

from .helpers import getAvgRatingOfRecipe
# import required data models
from .models import Recipe


# load login page
def login_view(request):
    return render(request, 'dist/login.html', {})


# called when user try to login - validate user logins and open dashboard page
def tryLogin(request):
    data = {}
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return JsonResponse({'msg': 'Login successful', 'url': '/dashboard'})
        else:
            data = {'msg': 'Invalid Username/Password', 'url': '/login'}
    return JsonResponse(data)


# load signup page
def signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password == confirm_password:
            if User.objects.filter(username=username).exists():
                return JsonResponse({'msg': 'Username already exists', 'url': '/signup'})
            else:
                user = User.objects.create_user(username=username, password=password)
                login(request, user)
                return JsonResponse({'msg': 'Signup successful', 'url': '/dashboard'})
        else:
            return JsonResponse({'msg': 'Passwords do not match', 'url': '/signup'})

    return render(request, 'dist/signup.html', {})


# called when user try to create user account - create new user and open dashboard page
def trySignUp(request):
    if request.method == 'POST':
        # get fields sent from front-end
        first_name = request.POST.get('FirstName')
        last_name = request.POST.get('LastName')
        username = request.POST.get('Username')
        email = request.POST.get('Email')
        password = request.POST.get('Password')
        confirm_password = request.POST.get('ConfirmPassword')

        # password validation
        if password != confirm_password:
            return JsonResponse({'msg': 'Passwords do not match'})
        # Username validation
        if User.objects.filter(username=username).exists():
            return JsonResponse({'msg': 'Username already exists'}, status=200)
        # Email validation
        if User.objects.filter(email=email).exists():
            return JsonResponse({'msg': 'Email already exists'}, status=200)

        # Create a new user object
        user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name, email=email,
                                        password=password)

        user.save()  # save in database and login it
        login(request, user)
        return JsonResponse({'url': '/dashboard'}, status=200)  # route user to dashbaord

    return JsonResponse({'msg': 'Invalid request'}, status=200)


# logout user from app
def logout_user(request):
    logout(request)
    return redirect('login')


# to ensure that the these views can only be accessed by authenticated users.
@login_required
def dashboard(request):
    return render(request, 'dist/dashboard.html', {'user': request.user})


# show user profile page
@login_required
def profile_view(request):
    # if request is post, it means user call view with update profile data, so update its profile
    if request.method == 'POST':
        first_name = request.POST.get('fname-column')
        last_name = request.POST.get('lname-column')
        user = request.user
        user.first_name = first_name
        user.last_name = last_name

        # Handle password update if provided
        new_password = request.POST.get('new-password-column')
        if new_password:
            user.set_password(new_password)  # set password
            user.save()
            # Log the user out to ensure they can log in with the new password
            logout(request)
            return redirect('login')  # Redirect to login page so that user log in again with the new password
        user.save()

    return render(request, 'dist/profile.html', {'user': request.user})


# to show all recipes to user
@login_required
def recipes(request):
    recipes = Recipe.objects.all()  # get all recipes from DB
    for recipe in recipes:
        if recipe.rating:  # Check if there are ratings
            average_rate = getAvgRatingOfRecipe(recipe)
        else:
            average_rate = 0
        recipe.rating = average_rate  # set avg rating

    # Sort recipes by the average rating in descending order (highest rating first)
    sorted_recipes = sorted(recipes, key=lambda x: x.rating, reverse=True)
    return render(request, 'dist/recipes.html', {'recipes': sorted_recipes, 'title': 'All Recipes'})


# to show user created recipes
@login_required
def my_recipe(request):
    # Filter recipes to show only those created by the logged user
    recipes = Recipe.objects.filter(user=request.user)
    if recipes:
        for recipe in recipes:
            if recipe.rating:  # Check if there are ratings
                average_rate = getAvgRatingOfRecipe(recipe)
            else:
                average_rate = 0
            recipe.rating = average_rate

        # Sort recipes by the average rating in descending order (highest rating first)
        sorted_recipes = sorted(recipes, key=lambda x: x.rating, reverse=True)
        return render(request, 'dist/recipes.html', {'recipes': sorted_recipes, 'title': 'My Recipes'})

    # if user has no recipes created, then show a proper msg to UI
    return render(request, 'dist/recipes.html', {'recipes': [], 'title': 'My Recipes',
                                                 'msg': "🍳 No recipes yet! Go to the Dashboard and tap 'Upload Recipe' to share your first dish! 🍲"})


# to show recipes liked by user
@login_required
def liked_recipe(request):
    # Filter recipes to show only those created by the logged-in user
    recipes = Recipe.objects.all()
    if recipes:
        recipes = [recipe for recipe in recipes if request.user.username in recipe.likes]
        for recipe in recipes:
            if recipe.rating:  # Check if there are ratings
                average_rate = getAvgRatingOfRecipe(recipe)
            else:
                average_rate = 0
            recipe.rating = average_rate

        # Sort recipes by the average rating in descending order (highest rating first)
        sorted_recipes = sorted(recipes, key=lambda x: x.rating, reverse=True)
        return render(request, 'dist/recipes.html', {'recipes': sorted_recipes, 'title': 'Liked Recipes'})

    # if user has no liked recipes, then show a proper msg to UI
    return render(request, 'dist/recipes.html', {'recipes': [], 'title': 'Liked Recipes',
                                                 'msg': "🍳 No liked recipes yet! Go to the Dashboard & tap 'Search Recipe' to add it to your liked list! 🍲"})


# to display details of a recipe
@login_required
def recipe_detail(request, recipe_id):
    # Fetch the recipe by ID or return a 404 if not found
    recipe = get_object_or_404(Recipe, RecipeId=recipe_id)

    # Prepare the context with recipe details, likes, and comments
    average_rate = 0
    if recipe.rating:  # Check if there are ratings
        average_rate = getAvgRatingOfRecipe(recipe)
    else:
        average_rate = 0
    recipe.rating = average_rate
    # set values to send to front-end
    content = {'recipe': recipe, 'likes_count': len(recipe.likes), 'comments_count': len(recipe.comments),
               'likes': recipe.likes, 'comments': recipe.comments, }

    # Render the template with the recipe content
    return render(request, 'dist/recipe_detail.html', content)


# to add a new recipe
@login_required
def add_recipe(request):
    user = request.user
    if request.method == 'POST':
        # get front-end values sent by user
        recipe_name = request.POST.get('RecipeName')
        origin = request.POST.get('Origin')
        ingredients = request.POST.get('Ingredients')
        image = request.FILES.get('image')
        rating = []
        duration = request.POST.get('duration')
        Procedure = request.POST.get('Procedure')

        # check null / empty values if any
        if not recipe_name or not origin or not ingredients or not duration:
            return render(request, 'dist/add_recipe.html', {'error': 'All fields are required'})
        # create object and store in db
        try:
            recipe = Recipe(RecipeName=recipe_name, Origin=origin, Ingredients=ingredients, image=image, rating=rating,
                            duration=duration,Procedure=Procedure, user=user  # Link to the logged-in user
                            )
            recipe.save()
            return redirect('dashboard')
        except Exception as e:
            # show proper error if new object is not saved in db
            return render(request, 'dist/add_recipe.html', {'error': f'Error saving recipe: {e}'})

    return render(request, 'dist/add_recipe.html')


# View for updating likes
@login_required
def like_recipe(request, recipe_id):
    # get recipe based on id
    recipe = get_object_or_404(Recipe, RecipeId=recipe_id)
    user_id = request.user.username  # Get current user ID
    if user_id not in recipe.likes:
        recipe.add_like(user_id)  # to add like
        action = 'liked'
    else:
        recipe.remove_like(user_id)  # to remove added like
        action = 'unliked'

    return JsonResponse({'success': True, 'action': action, 'like_count': len(recipe.likes)})


# View for adding comments
@login_required
def submit_comment(request, recipe_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)  # Parse the JSON data
            comment = data.get('text')  # Get the comment content from JSON

            # validate comment
            if not comment:
                return JsonResponse({'success': False, 'error': 'Comment cannot be empty'})
            # get recipe based on id
            recipe = get_object_or_404(Recipe, RecipeId=recipe_id)
            user_id = request.user.username  # Get the current user ID to store with comment
            recipe.add_comment(user_id, comment)  # to save in db

            return JsonResponse({'success': True, 'comment': comment, 'user_id': user_id})
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON format'})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'})


def getAvgRatingOfRecipe(recipe):
    # Find the sum of ratings and divide by total ratings
    avg_rating = sum(recipe.rating) / len(recipe.rating)
    # Return the rounded average rating to 1 decimal place e.g 3.4, 4.5
    return round(avg_rating, 1)
# to rate a recipe based on user experience
@login_required
def rate_recipe(request, recipe_id):
    if request.method == "POST":
        data = json.loads(request.body)
        rating = int(data.get('rating'))  # get rate value sent from front-end

        try:
            recipe = Recipe.objects.get(RecipeId=recipe_id)  # get recipe based on id
            # Update new rating here

            recipe.rating.append(rating)
            new_rate = getAvgRatingOfRecipe(recipe)  # get new avg. rating
            recipe.save()
            # send to front-end
            return JsonResponse({'success': True, 'new_rating': new_rate})
        except Recipe.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Recipe not found'}, status=404)

    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)
