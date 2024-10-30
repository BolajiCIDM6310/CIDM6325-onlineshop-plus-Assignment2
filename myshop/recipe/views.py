from django.core.mail import send_mail
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Count
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.http import require_POST, require_http_methods
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from .forms import UserRegistrationForm
from django.contrib.auth.models import User
from taggit.models import Tag
from django.utils import timezone
from datetime import timedelta
from django.urls import reverse
from cart.cart import Cart
from .models import SubscriptionPlan, RecipeBook, UserSubscription
from .forms import SubscriptionSelectForm, RecipeBookPurchaseForm
from django.http import HttpResponse
from cart.forms import CartAddProductForm
from .recommender import Recommender_rec
from .forms import (
    RecipeRatingForm,
    EmailRecipeForm,
    CommentRecForm,
)
from .models import Recipe, RecipeRating, BookmarkRecipe


def recipe_list(request, tag_slug=None):
    recipe_list = Recipe.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        recipe_list = recipe_list.filter(tags__in=[tag])

    # Pagination with 3 recipes per page
    paginator = Paginator(recipe_list, 3)  # Changed from post_list to recipe_list
    page_number = request.GET.get("page", 1)
    try:
        recipes = paginator.page(page_number)
    except PageNotAnInteger:
        # If page_number is not an integer get the first page
        recipes = paginator.page(1)
    except EmptyPage:
        # If page_number is out of range get last page of results
        recipes = paginator.page(paginator.num_pages)

    # return render(request, 'recipes/recipe_list.html', {'recipes': recipes, 'tag': tag})
    # print(tag)
    return render(request, "recipes/list.html", {"recipes": recipes, "tag": tag})


@login_required
def recipe_detail(request, year, month, day, slug, id):
    recipe = get_object_or_404(
        Recipe,
        status=Recipe.Status.PUBLISHED,
        id=id,
        slug=slug,
        publish__year=year,
        publish__month=month,
        publish__day=day,
    )

    # # Check for user subscription or book purchase
    # has_subscription = UserSubscription.objects.filter(
    #     user=request.user, recip=recipe
    # ).exists()
    # has_recipe_book = RecipeBook.objects.filter(
    #     user=request.user, recipe=recipe
    # ).exists()

    cart_recipe_form = CartAddProductForm()
    r = Recommender_rec()
    recommended_recipes = r.suggest_recipes_for([recipe], 4)

    ratings = recipe.ratings.all()
    user_rating = None
    if request.user.is_authenticated:
        user_rating = ratings.filter(user=request.user).first()

    rating_form = RecipeRatingForm()

    # List of active comments for this post
    comments = recipe.responses.filter(active=True)
    # Form for users to comment
    form = CommentRecForm()

    # List of similar posts
    recipe_tags_ids = recipe.tags.values_list("id", flat=True)
    similar_recipes = Recipe.published.filter(tags__in=recipe_tags_ids).exclude(
        id=recipe.id
    )
    similar_recipes = similar_recipes.annotate(same_tags=Count("tags")).order_by(
        "-same_tags", "-publish"
    )[:4]

    # bookmarking status
    is_bookmarked = False
    if request.user.is_authenticated:
        is_bookmarked = BookmarkRecipe.objects.filter(
            user=request.user, recipe=recipe
        ).exists()
    # return render(request, 'post_detail.html', {'post': post, 'is_bookmarked': is_bookmarked})

    # Check if the user has an active subscription
    has_subscription = (
        request.user.is_authenticated
        and UserSubscription.objects.filter(
            user=request.user, end_date__gt=timezone.now()
        ).exists()
    )

    # Check if the user owns the recipe book for this recipe
    has_recipe_book = (
        request.user.is_authenticated
        and RecipeBook.objects.filter(user=request.user, recipes=recipe).exists()
    )

    return render(
        request,
        "recipes/recipe_detail.html",
        {
            "recipe": recipe,
            "comments": comments,
            "form": form,
            "ratings": ratings,
            "user_rating": user_rating,
            "rating_form": rating_form,
            "is_bookmarked": is_bookmarked,
            "similar_recipes": similar_recipes,
            "has_subscription": has_subscription,
            "has_recipe_book": has_recipe_book,
            "cart_recipe_form": cart_recipe_form,
            "recommended_recipes": recommended_recipes,
        },
    )


def recipe_share(request, recipe_id):

    recipe = get_object_or_404(Recipe, id=recipe_id, status=Recipe.Status.PUBLISHED)
    sent = False

    if request.method == "POST":
        # Form was submitted
        form = EmailRecipeForm(request.POST)
        if form.is_valid():
            # Form fields passed validation
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(recipe.get_absolute_url())
            subject = (
                f"{cd['name']} ({cd['email']}) " f"recommends you read {recipe.title}"
            )
            message = (
                f"Read {recipe.title} at {post_url}\n\n"
                f"{cd['name']}'s comments: {cd['responses']}"
            )
            send_mail(
                subject=subject,
                message=message,
                from_email=None,
                recipient_list=[cd["to"]],
            )
            sent = True

    else:
        form = EmailRecipeForm()
    return render(
        request,
        "recipes/share.html",
        {"recipe": recipe, "form": form, "sent": sent},
    )


@require_http_methods(["GET", "POST"])
def recipe_comment(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id, status=Recipe.Status.PUBLISHED)
    comment = None
    # A comment was posted
    form = CommentRecForm(data=request.POST)
    if form.is_valid():
        # Create a Comment object without saving it to the database
        comment = form.save(commit=False)
        # Assign the post to the comment
        comment.recipe = recipe
        # Save the comment to the database
        comment.save()
    return render(
        request,
        "recipes/comment.html",
        {"recipe": recipe, "form": form, "comment": comment},
    )


# Helper function to get recipe by date and slug
def get_recipe_by_date_and_slug(year, month, day, slug):
    return get_object_or_404(
        Recipe, publish__year=year, publish__month=month, publish__day=day, slug=slug
    )


@login_required
def add_bookmark_rec(request, year, month, day, recipe):
    recipe = get_recipe_by_date_and_slug(year, month, day, recipe)
    BookmarkRecipe.objects.get_or_create(user=request.user, recipe=recipe)
    return redirect(recipe.get_absolute_url())


@login_required
def remove_bookmark_rec(request, year, month, day, recipe):
    recipe = get_recipe_by_date_and_slug(year, month, day, recipe)
    BookmarkRecipe.objects.filter(user=request.user, recipe=recipe).delete()
    return redirect(recipe.get_absolute_url())


@login_required
def view_bookmarks_rec(request):
    bookmarks = BookmarkRecipe.objects.filter(user=request.user).select_related(
        "recipe"
    )
    return render(request, "recipes/bookmarks.html", {"bookmarks": bookmarks})


# user registreation
def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("/")
    else:
        form = UserRegistrationForm()
    return render(request, "registration/register.html", {"form": form})


def recipe_book_checkout(request):
    if request.method == "POST":
        form = RecipeBookPurchaseForm(request.POST)
        if form.is_valid():
            book = form.cleaned_data["book"]
            cart = Cart(request)
            cart.clear()  # Clear any existing items in the cart
            cart.add(
                product=book,
                price=book.price,
            )
            request.session["recipe_book_id"] = book.id
            return redirect("payment:process")
    else:
        form = RecipeBookPurchaseForm()
    return render(request, "recipe/recipe_book_checkout.html", {"form": form})


@login_required
def purchase_subscription(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)

    # Get the subscription plan
    plan = SubscriptionPlan.objects.first()
    if not plan:
        # Handle the case where no subscription plan exists
        return HttpResponse(
            "No subscription plan available. Please contact support.", status=400
        )

    # Define the duration of the subscription (e.g., 30 days)
    subscription_duration = timedelta(days=30)

    # Calculate the end date for the subscription
    end_date = timezone.now() + subscription_duration

    # Check if an active subscription already exists
    subscription, created = UserSubscription.objects.get_or_create(
        user=request.user,
        defaults={"plan": plan, "start_date": timezone.now(), "end_date": end_date},
    )

    # If a subscription exists but is inactive, update it
    if not created and subscription.end_date <= timezone.now():
        subscription.start_date = timezone.now()
        subscription.end_date = end_date
        subscription.plan = plan
        subscription.save()

    # Redirect to the recipe detail view
    return redirect(
        reverse(
            "recipe:recipe_detail",
            args=[
                recipe.publish.year,
                recipe.publish.month,
                recipe.publish.day,
                recipe.slug,
            ],
        )
    )


# @login_required
# def purchase_recipe_book(request, recipe_id):
#     recipe = get_object_or_404(Recipe, id=recipe_id)
#     recipe_book, created = RecipeBook.objects.get_or_create(
#         user=request.user, recipe=recipe
#     )
#     if created:
#         Cart.objects.add_item(
#             recipe_book
#         )  # Assuming add_item method in Cart model for adding to cart
#     return redirect(
#         reverse(
#             "recipe:recipe_detail",
#             args=[
#                 recipe.publish.year,
#                 recipe.publish.month,
#                 recipe.publish.day,
#                 recipe.slug,
#             ],
#         )
#     )


# purchase_recipe_book view update
# @login_required
# def purchase_recipe_book(request, recipe_id):
#     recipe = get_object_or_404(Recipe, id=recipe_id)
#     recipe_book, created = RecipeBook.objects.get_or_create(
#         user=request.user, recipes=recipe  # Use the correct `recipes` field here
#     )
#     if created:
#         cart = Cart(request)  # Initialize the cart with the request
#         cart.add(
#             product=recipe_book,
#             price=recipe_book.price,  # Assuming a `price` attribute exists on `recipe`
#         )
#     return redirect(
#         reverse(
#             "recipe:recipe_detail",
#             args=[
#                 recipe.publish.year,
#                 recipe.publish.month,
#                 recipe.publish.day,
#                 recipe.slug,
#             ],
#         )
#     )


@login_required
def purchase_recipe_book(request, recipe_id):
    # Fetch the recipe
    recipe = get_object_or_404(Recipe, id=recipe_id)

    # Get or create the RecipeBook for the user without the `recipes` field
    recipe_book, created = RecipeBook.objects.get_or_create(user=request.user)

    # Add the recipe to the ManyToMany field if it’s not already associated
    recipe_book.recipes.add(recipe)

    # If the RecipeBook is newly created, add it to the cart
    if created:
        cart = Cart(request)  # Initialize the cart with the request
        cart.add(
            product=recipe_book,
            price=recipe_book.price,  # Assuming the `Recipe` model has a `price` attribute
        )

    # Redirect to the recipe detail view
    return redirect(
        reverse(
            "recipe:recipe_detail",
            args=[
                recipe.publish.year,
                recipe.publish.month,
                recipe.publish.day,
                recipe.slug,
            ],
        )
    )


# subscription_checkout view update
def subscription_checkout(request):
    if request.method == "POST":
        form = SubscriptionSelectForm(request.POST)
        if form.is_valid():
            plan = form.cleaned_data["plan"]
            cart = Cart(request)
            cart.clear()  # Clear any existing items in the cart
            cart.add(
                product=plan,
                price=plan.price,
            )
            request.session["subscription_plan_id"] = plan.id
            return redirect("payment:process")
    else:
        form = SubscriptionSelectForm()
    return render(request, "recipes/subscription_checkout.html", {"form": form})
