from django.contrib import admin
from .models import Comment, Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ["title", "slug", "author", "publish", "display_photo", "status"]
    list_filter = ["status", "created", "publish", "author"]
    search_fields = ["title", "body"]
    prepopulated_fields = {"slug": ("title",)}
    raw_id_fields = ["author"]
    date_hierarchy = "publish"
    ordering = ["status", "publish"]
    show_facets = admin.ShowFacets.ALWAYS

    def display_photo(self, obj):
        if obj.photo:
            return '<img src="{}" width="50" height="50" />'.format(obj.photo.url)
        return "No Image"

    display_photo.allow_tags = True
    display_photo.short_description = "Photo"


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "post", "created", "active"]
    list_filter = ["active", "created", "updated"]
    search_fields = ["name", "email", "body"]
