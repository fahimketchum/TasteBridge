from django.contrib.auth.models import User  # Import Django's built-in User model
from django.db import models

# We are using Django's built-in User model to store User data, so we only
# need to create Recipe model and create its relation with user model
class Recipe(models.Model):
    RecipeId = models.AutoField(primary_key=True)  # primary key
    RecipeName = models.CharField(max_length=50)
    Origin = models.CharField(max_length=200)
    Ingredients = models.CharField(max_length=200)
    image = models.FileField(upload_to='images/')
    rating = models.JSONField(blank=True, default=list)  # store ratings given by users
    duration = models.CharField(max_length=3)  # Store cooking time
    Procedure=models.TextField(default="")
    # Links Recipe to User; deletes related recipes if the User is deleted.
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipes')

    # Store Recipe's likes and comments as JSON data
    likes = models.JSONField(blank=True, default=list)
    comments = models.JSONField(blank=True, default=list)

    def add_like(self, user_id):
        # Add user_id to the likes list if not already present
        if user_id not in self.likes:
            self.likes.append(user_id)
            self.save()

    def remove_like(self, user_id):
        # Remove user_id from the likes list
        if user_id in self.likes:
            self.likes.remove(user_id)
            self.save()

    def add_comment(self, user_id, comment):
        # Add comment in dictionary format with user_id and comment msg
        comment = {'user_id': user_id, 'content': comment, }
        self.comments.append(comment)
        self.save()

    def remove_comment(self, comment_index):
        # Remove comment by its index
        if 0 <= comment_index < len(self.comments):
            self.comments.pop(comment_index)
            self.save()
