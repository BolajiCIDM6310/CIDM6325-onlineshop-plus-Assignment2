# import weasyprint
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.staticfiles import finders
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string

from cart.cart import Cart, Cart_rec
from .forms import OrderCreateForm
from .models import Order, OrderItem
from .tasks import order_created


def order_create(request):
    cart = Cart(request)
    if request.method == "POST":
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            if cart.coupon:
                order.coupon = cart.coupon
                order.discount = cart.coupon.discount
            order.save()
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item["product"],
                    price=item["price"],
                    quantity=item["quantity"],
                )
            # clear the cart
            cart.clear()
            # launch asynchronous task
            order_created.delay(order.id)
            # set the order in the session
            request.session["order_id"] = order.id
            # redirect for payment
            return redirect("payment:process")
    else:
        form = OrderCreateForm()
    return render(
        request,
        "orders/order/create.html",
        {"cart": cart, "form": form},
    )


@staff_member_required
def admin_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, "admin/orders/order/detail.html", {"order": order})


@staff_member_required
def admin_order_pdf(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    html = render_to_string("orders/order/pdf.html", {"order": order})
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f"filename=order_{order.id}.pdf"
    # weasyprint.HTML(string=html).write_pdf(
    # response,
    # stylesheets=[weasyprint.CSS(finders.find('css/pdf.css'))],
    # )
    return response


from recipe.models import SubscriptionPlan, RecipeBook, UserSubscription


def order_create2(request):
    cart = Cart_rec(request)
    if request.method == "POST":
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            # Set coupon and discount if applied
            if cart.coupon:
                order.coupon = cart.coupon
                order.discount = cart.coupon.discount
            order.save()

            for item in cart:
                if item["item_type"] == "SubscriptionPlan":
                    plan = SubscriptionPlan.objects.get(id=item["product_id"])
                    UserSubscription.objects.create(
                        user=request.user,
                        plan=plan,
                        start_date=timezone.now(),
                        end_date=timezone.now()
                        + timezone.timedelta(days=plan.duration_days),
                    )
                elif item["item_type"] == "RecipeBook":
                    book = RecipeBook.objects.get(id=item["product_id"])
                    OrderItem.objects.create(
                        order=order,
                        product=book,
                        price=item["price"],
                        quantity=item["quantity"],
                    )

            cart.clear()
            order_created.delay(order.id)
            request.session["order_id"] = order.id
            return redirect("payment:process")
    else:
        form = OrderCreateForm()
    return render(request, "orders/order/create.html", {"cart": cart, "form": form})
