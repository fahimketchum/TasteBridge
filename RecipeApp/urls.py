# Importing necessary modules for URL routing and views handling.
from django.urls import path
from . import views

# Authentication related paths.
auth_patterns = [
    path('', views.login_view, name='login'),  # Default login view
    path('login/', views.login_view, name='login'),  # Login page
    path('accounts/login/', views.login_view, name='login'),  # Login page
    path('tryLogin', views.tryLogin),  # Handle login functionality
    path('signup/', views.signup_view, name='signup'),  # Signup page
    path('trySignUp', views.trySignUp, name='trySignUp'),  # Handle signup functionality
    path('logout/', views.logout_user, name='logout'),  # Handle Logout functionality
]

# Dashboard and profile-related paths.
profile_patterns = [
    path('dashboard/', views.dashboard, name='dashboard'),  # Take user to dashboard page
    path('profile/', views.profile_view, name='profile_view'),  # Take user to profile page
]

# Recipe-related paths.
recipe_patterns = [
    path('recipes/', views.recipes, name='recipes'),  # To List of all recipes
    path('my_recipe/', views.my_recipe, name='my_recipe'),  # To show User's own recipes
    path('add_recipe/', views.add_recipe, name='add_recipe'),  # To Add a new recipe
    path('liked_recipe/', views.liked_recipe, name='liked_recipe'),  # To show User's liked recipes
    path('recipe/<int:recipe_id>/', views.recipe_detail, name='recipe_detail'),  # Open Recipe detail page
    path('recipe/<int:recipe_id>/like/', views.like_recipe, name='like_recipe'),  # Like a specific recipe
    path('recipe/<int:recipe_id>/comment/', views.submit_comment, name='submit_comment'), # Share feedback by adding comments for a recipe
    path('rate-recipe/<int:recipe_id>/', views.rate_recipe, name='rate_recipe'),  # Rate a recipe on the scale 1-5
]

# URL patterns for routing different views and pages in the recipe app
urlpatterns = auth_patterns + profile_patterns + recipe_patterns