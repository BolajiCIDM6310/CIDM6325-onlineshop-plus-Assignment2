from django.urls import path

from . import views

app_name = "cart"

urlpatterns = [
    path("", views.cart_detail, name="cart_detail"),
    path("rec/", views.cart_detail_rec, name="cart_detail_rec"),
    path("add/<int:product_id>/", views.cart_add, name="cart_add"),
    path("rec/add/<int:recipe_id>/", views.cart_add_rec, name="cart_add_rec"),
    path(
        "remove/<int:product_id>/",
        views.cart_remove,
        name="cart_remove",
    ),
    path(
        "rec/remove/<int:recipe_id>/",
        views.cart_remove_rec,
        name="cart_remove_rec",
    ),
]
