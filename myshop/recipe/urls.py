from django.urls import path
from . import views
from .feeds import LatestRecipesFeed

app_name = "recipe"

urlpatterns = [
    path("", views.recipe_list, name="recipe_list"),
    path("tag/<slug:tag_slug>/", views.recipe_list, name="recipe_list_by_tag"),
    path(
        "<int:year>/<int:month>/<int:day>/<slug:slug>/<int:id>/",
        views.recipe_detail,
        name="recipe_detail",
    ),
    path("<int:recipe_id>/share/", views.recipe_share, name="recipe_share"),
    path("<int:recipe_id>/comment/", views.recipe_comment, name="recipe_comment"),
    path("feed/", LatestRecipesFeed(), name="post_feed"),
    # Bookmark-related URLs using the same structure
    path("bookmarks/", views.view_bookmarks_rec, name="view_bookmarks_rec"),
    path(
        "<int:year>/<int:month>/<int:day>/<slug:recipe>/add/",
        views.add_bookmark_rec,
        name="add_bookmark_rec",
    ),
    path(
        "<int:year>/<int:month>/<int:day>/<slug:recipe>/remove/",
        views.remove_bookmark_rec,
        name="remove_bookmark_rec",
    ),
    path("subscribe/", views.subscription_checkout, name="subscription_checkout"),
    path("buy-book/", views.recipe_book_checkout, name="recipe_book_checkout"),
    path(
        "rec<int:recipe_id>/purchase-subscription/",
        views.purchase_subscription,
        name="purchase_subscription",
    ),
    path(
        "<int:recipe_id>/purchase-recipe-book/",
        views.purchase_recipe_book,
        name="purchase_recipe_book",
    ),
]
