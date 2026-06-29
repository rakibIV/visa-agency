from django import forms
from django.contrib.auth import get_user_model

from .models import Staff

User = get_user_model()


class StaffCreationForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=150,
        required=True,
    )

    last_name = forms.CharField(
        max_length=150,
        required=False,
    )

    email = forms.EmailField(
        required=False,
    )

    password = forms.CharField(
        widget=forms.PasswordInput(
            render_value=False,
        ),
        required=True,
    )

    class Meta:
        model = Staff

        exclude = (
            "user",
            "employee_id",
        )

    def clean_email(self):
        email = self.cleaned_data.get("email")

        if not email:
            return email

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "A user with this email already exists."
            )

        return email


class StaffChangeForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=150,
        required=True,
    )

    last_name = forms.CharField(
        max_length=150,
        required=False,
    )

    email = forms.EmailField(
        required=False,
    )

    new_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(
            render_value=False,
        ),
        help_text=(
            "Leave blank to keep the current password."
        ),
    )

    class Meta:
        model = Staff

        exclude = (
            "user",
        )

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(
            *args,
            **kwargs,
        )

        if self.instance.pk:
            self.fields["first_name"].initial = (
                self.instance.user.first_name
            )

            self.fields["last_name"].initial = (
                self.instance.user.last_name
            )

            self.fields["email"].initial = (
                self.instance.user.email
            )

    def clean_email(self):
        email = self.cleaned_data.get("email")

        if not email:
            return email

        queryset = User.objects.filter(
            email=email,
        ).exclude(
            pk=self.instance.user.pk,
        )

        if queryset.exists():
            raise forms.ValidationError(
                "A user with this email already exists."
            )

        return email