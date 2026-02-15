

######################

from django import forms
from django.contrib.auth.forms import UserCreationForm
# from .models import CustomUser, Idea, Event
from .models import CustomUser
from django.shortcuts import redirect
from .models import Post, Comment
from django import forms
from .models import UserProfile


from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from .models import Project, Attachment, Patent

##innovator page form

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'industry', 'description', 'website_link', 'image', 'status']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }
    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            # You can add some validation here if necessary, e.g., for file size or type
            pass
        return image

from .models import ProjectImage

class ProjectImageForm(forms.ModelForm):
    class Meta:
        model = ProjectImage
        fields = ['image', 'name', 'description']
        
        
class PatentForm(forms.ModelForm):
    class Meta:
        model = Patent
        fields = ['title', 'description', 'filed_date']

class AttachmentForm(forms.Form):
    attachments = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': False}), required=True)



##post form


# from django import forms


###registration
class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter first name'})
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter last name'})
    )
    phone_number = forms.CharField(
        max_length=15,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter phone number'})
    )

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'phone_number', 'email', 'password1', 'password2', 'user_type']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter password'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm password'}),
            'user_type': forms.Select(attrs={'class': 'form-control'})
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        
        # Generate the username as first_name.last_name (lowercase)
        user.username = f"{user.first_name.lower()}.{user.last_name.lower()}"

        # Ensure the username is unique
        counter = 1
        base_username = user.username
        while CustomUser.objects.filter(username=user.username).exists():
            user.username = f"{base_username}{counter}"
            counter += 1

        if commit:
            user.save()
        return user



# Event Form


#Posts form

# from django import forms
class ContactForm(forms.Form):
    name = forms.CharField(
        max_length=100, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Name'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Your Email'})
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Your Message', 'rows': 4})
    )

##login form

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(label="Username or Email", max_length=254)

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if "@" in username:
            # If the input contains an "@" symbol, it's likely an email
            try:
                user = get_user_model().objects.get(email=username)
                return user.username  # Return the username associated with the email
            except get_user_model().DoesNotExist:
                raise ValidationError("No user found with this email address.")
        return username



##profile update
class ProfileUpdateForm(forms.ModelForm):
    # Fields from CustomUser
    first_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter first name'})
    )
    bio = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Tell us about yourself...', 'rows': 4})
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'profile_pics']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter username'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email'}),
            'profile_pics': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.get('instance')  # instance is a CustomUser
        super().__init__(*args, **kwargs)

        # Set initial value of bio from UserProfile
        if self.user and hasattr(self.user, 'userprofile'):
            self.fields['bio'].initial = self.user.userprofile.bio

    def clean_first_name(self):
        # Ensure first name is always the same as the username
        if self.cleaned_data.get('first_name') != self.cleaned_data.get('username'):
            self.cleaned_data['first_name'] = self.cleaned_data['username']
        return self.cleaned_data['first_name']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data.get('username')

        if commit:
            user.save()
            # Save bio to user profile
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.bio = self.cleaned_data.get('bio')
            profile.save()
        return user


##Edit profile form


##change pass and names in profile


class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label="Old Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter current password'})
    )
    new_password1 = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter new password'})
    )
    new_password2 = forms.CharField(
        label="Confirm New Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm new password'})
    )

    class Meta:
        model = CustomUser
        fields = ['old_password', 'new_password1', 'new_password2']

####################
# ##profile edit
class EditProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['profile_pics', 'phone_number', 'bio', 'industry', 'company']


class ProfileEditForm(forms.ModelForm):
    first_name = forms.CharField(max_length=50, required=True)
    last_name = forms.CharField(max_length=50, required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'profile_pics','bio', 'industry', 'company']

    class Meta:
        model = UserProfile
        # fields = ['profile_pics', 'phone_number', 'bio', 'industry', 'company']
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'profile_pics','bio', 'industry', 'company']

        widgets = {
            'industry': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email

    def save(self, commit=True):
        profile = super().save(commit=False)
        user = profile.user
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            profile.save()
        return profile


##Message form
from .models import Message
class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Type your message here...'})
        }