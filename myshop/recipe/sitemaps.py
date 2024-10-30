from django.contrib.sitemaps import Sitemap

from .models import Recipe


class RecipeSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.9

    def items(self):
        return Recipe.published.all()

    def lastmod(self, obj):
        return obj.updated
