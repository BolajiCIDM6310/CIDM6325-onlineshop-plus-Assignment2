from django.urls import path
from . import views
from .feeds import LatestPostsFeed

app_name = "blog"

urlpatterns = [
    # Post views
    path("", views.post_list, name="post_list"),
    path("tag/<slug:tag_slug>/", views.post_list, name="post_list_by_tag"),
    path(
        "<int:year>/<int:month>/<int:day>/<slug:post>/",
        views.post_detail,
        name="post_detail",
    ),
    path("<int:post_id>/share/", views.post_share, name="post_share"),
    path("<int:post_id>/comment/", views.post_comment, name="post_comment"),
    path("feed/", LatestPostsFeed(), name="post_feed"),
    # Bookmark-related URLs using the same structure
    path("bookmarks/", views.view_bookmarks, name="view_bookmarks"),
    path(
        "<int:year>/<int:month>/<int:day>/<slug:post>/add/",
        views.add_bookmark,
        name="add_bookmark",
    ),
    path(
        "<int:year>/<int:month>/<int:day>/<slug:post>/remove/",
        views.remove_bookmark,
        name="remove_bookmark",
    ),
]
