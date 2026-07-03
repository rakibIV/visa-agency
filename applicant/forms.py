from django import forms
from decimal import Decimal
from .models import (
    AgreementTemplate,
    Applicant,
    ApplicantAddress,
    ApplicantDocument,
    ApplicantNote,
    ApplicantPayment,
    ApplicantProfile,
    ApplicantTag,
    ApplicationStatus,
)
from .services import (
    create_applicant,
    update_applicant,
    create_payment,
    update_payment,
    upload_document,
    update_document,
    

)


class ApplicantCreateForm(forms.ModelForm):

    class Meta:
        model = Applicant

        exclude = [
            "application_id",
            "created_by",
            "updated_by",
            "deleted_at",
            "is_deleted",
            "created_at",
            "updated_at",
        ]

    def save(self, commit=True):

        if not commit:
            raise ValueError(
                "ApplicantCreateForm requires commit=True."
            )

        applicant = create_applicant(
            **self.cleaned_data,
        )

        return applicant


class ApplicantUpdateForm(forms.ModelForm):

    class Meta:
        model = Applicant

        exclude = [
            "application_id",
            "created_by",
            "updated_by",
            "deleted_at",
            "is_deleted",
            "created_at",
            "updated_at",
        ]

    def save(self, commit=True):

        if not commit:
            raise ValueError(
                "ApplicantUpdateForm requires commit=True."
            )

        applicant = update_applicant(
            applicant=self.instance,
            **self.cleaned_data,
        )

        return applicant


class ApplicantProfileForm(forms.ModelForm):

    class Meta:
        model = ApplicantProfile

        exclude = [
            "created_at",
            "updated_at",
        ]

        widgets = {
            "date_of_birth": forms.DateInput(
                attrs={
                    "type": "date",
                }
            ),
        }

    def clean_phone(self):

        phone = self.cleaned_data.get(
            "phone",
        )

        if phone:
            phone = phone.strip()

        return phone

    def clean_email(self):

        email = self.cleaned_data.get(
            "email",
        )

        if email:
            email = email.lower()

        return email
    

class ApplicantAddressForm(forms.ModelForm):

    class Meta:
        model = ApplicantAddress

        exclude = [
            "created_at",
            "updated_at",
        ]

    def clean_extra_fields(self):

        data = self.cleaned_data.get(
            "extra_fields"
        )

        return data or {}


class ApplicantPaymentForm(forms.ModelForm):

    class Meta:
        model = ApplicantPayment

        exclude = [
            "currency_rate",
            "payment_number",
            "exchange_rate",
            "euro_amount",
            "created_at",
            "updated_at",
        ]

        widgets = {
            "payment_date": forms.DateInput(
                attrs={
                    "type": "date",
                }
            ),
        }

    def clean_amount(self):

        amount = self.cleaned_data.get(
            "amount"
        )

        if amount <= Decimal("0"):
            raise forms.ValidationError(
                "Amount must be greater than zero."
            )

        return amount

    def save(self, commit=True):

        if not commit:
            raise ValueError(
                "ApplicantPaymentForm requires commit=True."
            )

        if self.instance.pk:

            payment = update_payment(
                payment=self.instance,
                **self.cleaned_data,
            )

        else:

            payment = create_payment(
                **self.cleaned_data,
            )

        return payment


class ApplicantDocumentForm(forms.ModelForm):

    class Meta:
        model = ApplicantDocument

        exclude = [
            "verified",
            "verified_by",
            "verified_at",
            "created_at",
            "updated_at",
        ]

    def clean_title(self):

        title = self.cleaned_data.get(
            "title",
            "",
        ).strip()

        document_type = self.cleaned_data.get(
            "document_type",
        )

        if (
            document_type == "OTHER"
            and not title
        ):
            raise forms.ValidationError(
                "Title is required for Other document."
            )

        return title

    def save(self, commit=True):

        if not commit:
            raise ValueError(
                "ApplicantDocumentForm requires commit=True."
            )

        if self.instance.pk:

            document = update_document(
                document=self.instance,
                **self.cleaned_data,
            )

        else:

            document = upload_document(
                **self.cleaned_data,
            )

        return document
    


class ApplicantNoteForm(forms.ModelForm):

    class Meta:
        model = ApplicantNote

        exclude = [
            "created_at",
            "updated_at",
        ]

        widgets = {
            "note": forms.Textarea(
                attrs={
                    "rows": 5,
                }
            ),
        }

    def clean_note(self):

        note = self.cleaned_data.get(
            "note",
            "",
        ).strip()

        if not note:
            raise forms.ValidationError(
                "Note cannot be empty."
            )

        return note


class ApplicationStatusForm(forms.ModelForm):

    class Meta:
        model = ApplicationStatus

        fields = "__all__"

    def clean(self):

        cleaned_data = super().clean()

        is_default = cleaned_data.get(
            "is_default",
        )

        if is_default:

            queryset = (
                ApplicationStatus.objects.filter(
                    is_default=True,
                )
            )

            if self.instance.pk:

                queryset = queryset.exclude(
                    pk=self.instance.pk,
                )

            if queryset.exists():

                raise forms.ValidationError(
                    "Only one default status is allowed."
                )

        return cleaned_data


class ApplicantTagForm(forms.ModelForm):

    class Meta:
        model = ApplicantTag

        fields = "__all__"


class AgreementTemplateForm(forms.ModelForm):

    class Meta:
        model = AgreementTemplate

        fields = "__all__"

        widgets = {
            "body": forms.Textarea(
                attrs={
                    "rows": 18,
                }
            ),
        }

    def clean_body(self):

        body = self.cleaned_data.get(
            "body",
            "",
        ).strip()

        if not body:

            raise forms.ValidationError(
                "Agreement body cannot be empty."
            )

        return body
