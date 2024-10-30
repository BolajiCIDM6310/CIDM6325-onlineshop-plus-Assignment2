from coupons.forms import CouponApplyForm
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from shop.models import Product
from recipe.models import Recipe
from shop.recommender import Recommender
from recipe.recommender import Recommender_rec
from .cart import Cart, Cart_rec
from .forms import CartAddProductForm
from django.conf import settings


@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    form = CartAddProductForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        cart.add(
            product=product,
            quantity=cd["quantity"],
            override_quantity=cd["override"],
        )
    return redirect("cart:cart_detail")


@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect("cart:cart_detail")


def cart_detail(request):
    cart = Cart(request)
    for item in cart:
        item["update_quantity_form"] = CartAddProductForm(
            initial={"quantity": item["quantity"], "override": True}
        )
    coupon_apply_form = CouponApplyForm()

    r = Recommender()
    cart_products = [item["product"] for item in cart]
    if cart_products:
        recommended_products = r.suggest_products_for(cart_products, max_results=4)
    else:
        recommended_products = []

    return render(
        request,
        "cart/detail.html",
        {
            "cart": cart,
            "coupon_apply_form": coupon_apply_form,
            "recommended_products": recommended_products,
        },
    )


@require_POST
def cart_add_rec(request, recipe_id):
    cart_rec = Cart_rec(request)
    print(recipe_id)
    print(cart_rec.cart_rec)
    recipe = get_object_or_404(Recipe, id=recipe_id)
    form = CartAddProductForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        cart_rec.add(
            recipe=recipe,
            quantity=cd["quantity"],
            override_quantity=cd["override"],
        )
    return redirect("cart:cart_detail_rec")


@require_POST
def cart_remove_rec(request, recipe_id):
    cart_rec = Cart_rec(request)
    recipe = get_object_or_404(Recipe, id=recipe_id)
    cart_rec.remove(recipe)
    return redirect("cart:cart_detail_rec")


def cart_detail_rec(request):
    cart_rec = Cart_rec(request)
    for item in cart_rec:
        item["update_quantity_form"] = CartAddProductForm(
            initial={"quantity": item["quantity"], "override": True}
        )
    coupon_apply_form = CouponApplyForm()

    r = Recommender_rec()
    cart_recipes = [item["recipe"] for item in cart_rec]
    if cart_recipes:
        recommended_recipes = r.suggest_recipes_for(cart_recipes, max_results=4)
    else:
        recommended_recipes = []

    return render(
        request,
        "cart/detail_rec.html",
        {
            "cart_rec": cart_rec,
            "coupon_apply_form": coupon_apply_form,
            "recommended_recipes": recommended_recipes,
        },
    )

    # @require_POST
    # def cart_add_rec(request, recipe_id):
    cart = Cart_rec(request)

    recipe = get_object_or_404(Recipe, id=recipe_id)
    form = CartAddProductForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        cart.add(
            recipe=recipe,
            quantity=cd["quantity"],
            override_quantity=cd["override"],
        )
    print("Cart contents after adding:", cart.cart_rec)
    print(
        "Session data after adding recipe:",
        request.session[settings.CART_REC_SESSION_ID],
    )

    return redirect("cart:cart_detail_rec")
