from decimal import Decimal
from coupons.models import Coupon
from django.conf import settings
from shop.models import Product
from recipe.models import Recipe
import logging


class Cart:
    def __init__(self, request):
        """ss
        Initialize the cart.
        """
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            # save an empty cart in the session
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart
        # store current applied coupon
        self.coupon_id = self.session.get("coupon_id")

    def __iter__(self):
        """
        Iterate over the items in the cart and get the products
        from the database.
        """
        product_ids = self.cart.keys()
        # get the product objects and add them to the cart
        products = Product.objects.filter(id__in=product_ids)
        cart = self.cart.copy()
        for product in products:
            cart[str(product.id)]["product"] = product
        for item in cart.values():
            item["price"] = Decimal(item["price"])
            item["total_price"] = item["price"] * item["quantity"]
            yield item

    def __len__(self):
        """
        Count all items in the cart.
        """
        return sum(item["quantity"] for item in self.cart.values())

    def add(self, product, quantity=1, override_quantity=False):
        """
        Add a product to the cart or update its quantity.
        """
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {
                "quantity": 0,
                "price": str(product.price),
            }
        if override_quantity:
            self.cart[product_id]["quantity"] = quantity
        else:
            self.cart[product_id]["quantity"] += quantity
        self.save()

    def save(self):
        # mark the session as "modified" to make sure it gets saved
        self.session.modified = True

    def remove(self, product):
        """
        Remove a product from the cart.
        """
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def clear(self):
        # remove cart from session
        del self.session[settings.CART_SESSION_ID]
        self.save()

    def get_total_price(self):
        return sum(
            Decimal(item["price"]) * item["quantity"] for item in self.cart.values()
        )

    @property
    def coupon(self):
        if self.coupon_id:
            try:
                return Coupon.objects.get(id=self.coupon_id)
            except Coupon.DoesNotExist:
                pass
        return None

    def get_discount(self):
        if self.coupon:
            return (self.coupon.discount / Decimal(100)) * self.get_total_price()
        return Decimal(0)

    def get_total_price_after_discount(self):
        return self.get_total_price() - self.get_discount()


class Cart_rec:
    def __init__(self, request):
        """ss
        Initialize the cart.
        """
        self.session = request.session
        cart_rec = self.session.get(settings.CART_REC_SESSION_ID)
        if not cart_rec:
            # save an empty cart in the session
            cart_rec = self.session[settings.CART_REC_SESSION_ID] = {}
        self.cart_rec = cart_rec
        # store current applied coupon
        self.coupon_id = self.session.get("coupon_id")

    def __iter__(self):
        """
        Iterate over the items in the cart and get the products
        from the database.
        """
        recipe_ids = self.cart_rec.keys()
        # get the product objects and add them to the cart
        recipes = Recipe.objects.filter(id__in=recipe_ids)
        cart_rec = self.cart_rec.copy()
        for recipe in recipes:
            cart_rec[str(recipe.id)]["recipe"] = recipe
        for item in cart_rec.values():
            item["price"] = Decimal(item["price"])
            item["total_price"] = item["price"] * item["quantity"]
            yield item

    def __len__(self):
        """
        Count all items in the cart.
        """
        return sum(item["quantity"] for item in self.cart_rec.values())

    def add(self, recipe, quantity=1, override_quantity=False):
        """
        Add a recipe to the cart or update its quantity.
        """
        recipe_id = str(recipe.id)
        print("recipe id is ...", recipe_id)
        if recipe_id not in self.cart_rec:
            self.cart_rec[recipe_id] = {
                "quantity": 0,
                "price": str(recipe.price),
            }
        if override_quantity:
            self.cart_rec[recipe_id]["quantity"] = quantity
        else:
            self.cart_rec[recipe_id]["quantity"] += quantity
        self.save()

    def save(self):
        # mark the session as "modified" to make sure it gets saved
        self.session.modified = True

    def remove(self, recipe):
        """
        Remove a recipe from the cart.
        """
        recipe_id = str(recipe.id)
        if recipe_id in self.cart_rec:
            del self.cart_rec[recipe_id]
            self.save()

    def clear(self):
        # remove cart from session
        del self.session[settings.CART_REC_SESSION_ID]
        self.save()

    def get_total_price(self):
        return sum(
            Decimal(item["price"]) * item["quantity"] for item in self.cart_rec.values()
        )

    @property
    def coupon(self):
        if self.coupon_id:
            try:
                return Coupon.objects.get(id=self.coupon_id)
            except Coupon.DoesNotExist:
                pass
        return None

    def get_discount(self):
        if self.coupon:
            return (self.coupon.discount / Decimal(100)) * self.get_total_price()
        return Decimal(0)

    def get_total_price_after_discount(self):
        return self.get_total_price() - self.get_discount()
