import redis
from django.conf import settings

from .models import Recipe

# connect to redis
r = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
)


class Recommender_rec:
    def get_recipe_key(self, id):
        return f"recipe:{id}:purchased_with"

    def recipes_bought(self, recipes):
        recipe_ids = [p.id for p in recipes]
        for recipe_id in recipe_ids:
            for with_id in recipe_ids:
                # get the other recipes bought with each recipe
                if recipe_id != with_id:
                    # increment score for recipe purchased together
                    r.zincrby(self.get_recipe_key(recipe_id), 1, with_id)

    def suggest_recipes_for(self, recipes, max_results=6):
        recipe_ids = [p.id for p in recipes]
        if len(recipes) == 1:
            # only 1 recipe
            suggestions = r.zrange(
                self.get_recipe_key(recipe_ids[0]), 0, -1, desc=True
            )[:max_results]
        else:
            # generate a temporary key
            flat_ids = "".join([str(id) for id in recipe_ids])
            tmp_key = f"tmp_{flat_ids}"
            # multiple recipes, combine scores of all recipes
            # store the resulting sorted set in a temporary key
            keys = [self.get_recipe_key(id) for id in recipe_ids]
            r.zunionstore(tmp_key, keys)
            # remove ids for the recipes the recommendation is for
            r.zrem(tmp_key, *recipe_ids)
            # get the recipe ids by their score, descendant sort
            suggestions = r.zrange(tmp_key, 0, -1, desc=True)[:max_results]
            # remove the temporary key
            r.delete(tmp_key)
        suggested_recipes_ids = [int(id) for id in suggestions]
        # get suggested recipes and sort by order of appearance
        suggested_recipes = list(Recipe.objects.filter(id__in=suggested_recipes_ids))
        suggested_recipes.sort(key=lambda x: suggested_recipes_ids.index(x.id))
        return suggested_recipes

    def clear_purchases(self):
        for id in Recipe.objects.values_list("id", flat=True):
            r.delete(self.get_recipe_key(id))
