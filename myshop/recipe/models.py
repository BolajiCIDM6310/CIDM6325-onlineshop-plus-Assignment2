from django.core.validators import MinValueValidator
from decimal import Decimal
from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User
from taggit.managers import TaggableManager


class PublishedRecipeManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status=Recipe.Status.PUBLISHED)


class Recipe(models.Model):
    class Status(models.TextChoices):
        DRAFT = "DF", "Draft"
        PUBLISHED = "PB", "Published"

    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250, unique_for_date="publish")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="recipes",
    )
    ingredients = models.TextField()
    steps = models.TextField()
    cooking_time = models.PositiveIntegerField()  # Time in minutes
    publish = models.DateTimeField(default=timezone.now)
    photo = models.ImageField(upload_to="recipes/%Y/%m/%d/", blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=50)
    available = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=2, choices=Status, default=Status.DRAFT)

    objects = models.Manager()  # The default manager.
    published = PublishedRecipeManager()  # Our custom manager.

    tags = TaggableManager()  # For categorizing cuisines

    class Meta:
        ordering = ["-publish"]
        indexes = [
            models.Index(fields=["-publish"]),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse(
            "recipe:recipe_detail",
            # 'recipes/recipe_detail',
            args=[
                self.publish.year,
                self.publish.month,
                self.publish.day,
                self.slug,
                self.id,
            ],
        )


class BookmarkRecipe(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "recipe")


class CommentRes(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="responses"
    )
    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["created"]
        indexes = [
            models.Index(fields=["created"]),
        ]

    def __str__(self):
        return f"Comment by {self.name} on {self.recipe}"


class RecipeRating(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="ratings")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()  # Rating out of 5
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [
            "recipe",
            "user",
        ]  # Prevents a user from rating the same recipe multiple times

    def __str__(self):
        return f"{self.rating} by {self.user} for {self.recipe.title}"


# class RecipeBook(models.Model):
#     title = models.CharField(max_length=255)
#     description = models.TextField()
#     price = models.DecimalField(
#         max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.00"))]
#     )
#     created = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.title


class RecipeBook(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="recipe_books"
    )
    recipes = models.ManyToManyField("Recipe")
    purchased_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Recipe Book"


class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.00"))]
    )
    duration_days = models.PositiveIntegerField(help_text="Duration in days")
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class UserSubscription(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="subscriptions"
    )
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField()

    def is_active(self):
        return timezone.now() < self.end_date
