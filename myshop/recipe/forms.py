from django import forms
from .models import CommentRes, RecipeRating
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from .models import SubscriptionPlan, RecipeBook


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")


# end account


class EmailRecipeForm(forms.Form):
    name = forms.CharField(max_length=25)
    email = forms.EmailField()
    to = forms.EmailField()
    responses = forms.CharField(required=False, widget=forms.Textarea)


class CommentRecForm(forms.ModelForm):
    class Meta:
        model = CommentRes
        fields = ["name", "email", "body"]


class RecipeRatingForm(forms.ModelForm):
    class Meta:
        model = RecipeRating
        fields = ["rating"]


class SubscriptionSelectForm(forms.Form):
    plan = forms.ModelChoiceField(
        queryset=SubscriptionPlan.objects.all(), label="Choose a subscription plan"
    )


class RecipeBookPurchaseForm(forms.Form):
    book = forms.ModelChoiceField(
        queryset=RecipeBook.objects.all(), label="Choose a recipe book"
    )
