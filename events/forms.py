from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile

# Tailwind input classes
TAILWIND_INPUT = (
    "w-full px-4 py-3 rounded-xl bg-gray-50 dark:bg-gray-900 "
    "border border-gray-300 dark:border-gray-700 "
    "focus:ring-primary/40 focus:outline-none"
)

TAILWIND_FILE_INPUT = (
    "block w-full text-sm text-gray-700 dark:text-gray-300 "
    "bg-gray-50 dark:bg-gray-900 border border-gray-300 "
    "dark:border-gray-700 rounded-xl cursor-pointer"
)


# ------------------------------
# USER UPDATE FORM (basic details)
# ------------------------------
class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=150, required=False)
    last_name = forms.CharField(max_length=150, required=False)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({
                "class": TAILWIND_INPUT
            })


# ------------------------------
# PROFILE UPDATE FORM (UserProfile Model)
# ------------------------------
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('mobile', 'profile_picture')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            if field_name == "profile_picture":
                field.widget.attrs.update({"class": TAILWIND_FILE_INPUT})
            else:
                field.widget.attrs.update({"class": TAILWIND_INPUT})


# ------------------------------
# CUSTOM REGISTRATION FORM (Tailwind styled)
# ------------------------------
class CustomRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({
                "class": TAILWIND_INPUT
            })

            # Optional placeholders
            if name == "username":
                field.widget.attrs["placeholder"] = "Enter your username"
            if name == "password1":
                field.widget.attrs["placeholder"] = "Enter your password"
            if name == "password2":
                field.widget.attrs["placeholder"] = "Re-enter your password"
