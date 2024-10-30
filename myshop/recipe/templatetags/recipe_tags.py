from django import template
from ..models import Recipe
from django.db.models import Count
import markdown
from django.utils.safestring import mark_safe

register = template.Library()


# Recipe Tags
@register.simple_tag
def total_recipes():
    """Returns the total number of published recipes"""
    return Recipe.objects.filter(status=Recipe.Status.PUBLISHED).count()


@register.inclusion_tag("recipes/latest_recipes.html")
def show_latest_recipes(count=5):
    latest_recipes = Recipe.published.order_by("-publish")[:count]
    return {"latest_recipes": latest_recipes}


@register.simple_tag
def get_most_commented_recipes(count=5):
    """Returns the most commented recipes"""
    return (
        Recipe.objects.filter(status=Recipe.Status.PUBLISHED)
        .annotate(total_responses=Count("responses"))
        .order_by("-total_responses")[:count]
    )


@register.filter(name="markdown")
def markdown_format(text):
    return mark_safe(markdown.markdown(text))
