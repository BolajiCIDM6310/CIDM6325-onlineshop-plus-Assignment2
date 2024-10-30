import markdown
from django.contrib.syndication.views import Feed
from django.template.defaultfilters import truncatewords_html
from django.urls import reverse_lazy

from .models import Recipe


class LatestRecipesFeed(Feed):
    title = "Recipes"
    link = reverse_lazy("blog:recipe_list")
    description = "New Recipes Found."

    def items(self):
        return Recipe.published.all()[:5]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return truncatewords_html(markdown.markdown(item.ingredients), 80)

    def item_pubdate(self, item):
        return item.publish
