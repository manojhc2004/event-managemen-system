from django import forms
from django.contrib.auth.models import User
from .models import UserProfile

# Form for the default User model fields
class UserUpdateForm(forms.ModelForm):
    """Allows users to update basic User model fields."""
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=150, required=False)
    last_name = forms.CharField(max_length=150, required=False)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            
# Form for the extended UserProfile model fields
class ProfileUpdateForm(forms.ModelForm):
    """Allows users to update the custom UserProfile model fields."""
    class Meta:
        model = UserProfile
        fields = ('mobile', 'profile_picture')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            # Apply form-control only to mobile field, file input is handled differently
            if field_name != 'profile_picture':
                field.widget.attrs['class'] = 'form-control'