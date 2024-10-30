from django.contrib import admin
from parler.admin import TranslatableAdmin

from .models import (
    Recipe,
    RecipeRating,
    CommentRes,
    SubscriptionPlan,
    RecipeBook,
    UserSubscription,
)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "slug",
        "author",
        "publish",
        "price",
        "display_photo",
        "status",
    ]
    list_filter = ["status", "created", "publish", "author"]
    search_fields = ["title", "ingredients", "steps"]
    prepopulated_fields = {"slug": ("title",)}
    raw_id_fields = ["author"]
    date_hierarchy = "publish"
    ordering = ["status", "publish"]

    def display_photo(self, obj):
        if obj.photo:
            return '<img src="{}" width="50" height="50" />'.format(obj.photo.url)
        return "No Image"

    display_photo.allow_tags = True
    display_photo.short_description = "Photo"


@admin.register(CommentRes)
class CommentResAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "recipe", "created", "active"]
    list_filter = ["active", "created", "updated"]
    search_fields = ["name", "email", "body"]


@admin.register(RecipeRating)
class RecipeRatingAdmin(admin.ModelAdmin):
    list_display = ["recipe", "user", "rating", "created"]


# @admin.register(SubscriptionPlan)
# class SubscriptionPlanAdmin(TranslatableAdmin):
#     list_display = [
#         "name",
#         "description",
#         "price",
#         "duration_days",
#         "created",
#     ]
#     list_filter = ["price", "duration_days", "created"]
#     list_editable = ["description", "price", "duration_days"]


# @admin.register(RecipeBook)
# class RecipeBookAdmin(TranslatableAdmin):
#     list_display = [
#         "name",
#         "recipes",
#         "purchased_at",
#     ]
#     list_filter = ["user", "purchased_at"]


# @admin.register(UserSubscription)
# class UserSubscriptionAdmin(TranslatableAdmin):
#     list_display = [
#         "name",
#         "plan",
#         "start_date",
#         "end_date",
#     ]
#     list_filter = ["plan", "start_date", "end_date"]
#     list_editable = ["plan"]
