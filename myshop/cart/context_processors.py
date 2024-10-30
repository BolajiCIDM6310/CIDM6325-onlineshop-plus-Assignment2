from .cart import Cart
from .cart import Cart_rec


def cart(request):
    return {"cart": Cart(request)}


def cart_rec(request):
    return {"cart_rec": Cart_rec(request)}
