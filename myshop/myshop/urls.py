"""
URL configuration for myshop project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib.auth import views as auth_views
from django.contrib.sitemaps.views import sitemap
from blog.sitemaps import PostSitemap
from recipe.sitemaps import RecipeSitemap
from blog import views
from recipe import views

from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.utils.translation import gettext_lazy as _
from payment import webhooks


sitemaps = {
    "posts": PostSitemap,
}
sitemaps = {
    "recipes": RecipeSitemap,
}

urlpatterns = i18n_patterns(
    path("admin/", admin.site.urls),
    path(_("cart/"), include("cart.urls", namespace="cart")),
    path(_("orders/"), include("orders.urls", namespace="orders")),
    path(_("payment/"), include("payment.urls", namespace="payment")),
    path(_("coupons/"), include("coupons.urls", namespace="coupons")),
    path("rosetta/", include("rosetta.urls")),
    path("", include("shop.urls", namespace="shop")),
)

urlpatterns += [
    path(
        "payment/webhook/",
        webhooks.stripe_webhook,
        name="stripe-webhook",
    ),
    # path("admin/", admin.site.urls),
    path("blog/", include(("blog.urls", "blog"), namespace="blog")),
    path("rec/", include(("recipe.urls", "recipe"), namespace="recipe")),
    # Authentication URLs
    path("accounts/login/", auth_views.LoginView.as_view(), name="login"),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
    path(
        "accounts/password_change/",
        auth_views.PasswordChangeView.as_view(),
        name="password_change",
    ),
    path(
        "accounts/password_change/done/",
        auth_views.PasswordChangeDoneView.as_view(),
        name="password_change_done",
    ),
    path(
        "accounts/password_reset/",
        auth_views.PasswordResetView.as_view(),
        name="password_reset",
    ),
    path(
        "accounts/password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "accounts/reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "accounts/reset/done/",
        auth_views.PasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
    # path(
    #     "accounts/", include("django.contrib.auth.urls")
    # ),  # Include the default auth URLs
    path("accounts/register/", views.register, name="register"),
    # end auth
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),


    
    path('account/', include('account.urls')),
    path(
        'social-auth/',
        include('social_django.urls', namespace='social'),
    ),
    path('images/', include('images.urls', namespace='images')),
    path('__debug__/', include('debug_toolbar.urls')),

    # path("account/", include("account.urls")),
    # path(
    #     "social-auth/",
    #     include("social_django.urls", namespace="social"),
    # ),
    # path("images/", include("images.urls", namespace="images")),
    # path("__debug__/", include("debug_toolbar.urls")),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
