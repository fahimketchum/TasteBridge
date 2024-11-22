#  this file contains custom methods uses by recipe app

def getAvgRatingOfRecipe(recipe):
    # Find the sum of ratings and divide by total ratings
    avg_rating = sum(recipe.rating) / len(recipe.rating)
    # Return the rounded average rating to 1 decimal place e.g 3.4, 4.5
    return round(avg_rating, 1)