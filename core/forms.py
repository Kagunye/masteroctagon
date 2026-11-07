from django import forms

from .models import Enquiry


class ContactForm(forms.ModelForm):
    website = forms.CharField(required=False, widget=forms.HiddenInput)  # honeypot

    class Meta:
        model = Enquiry
        fields = ["name", "company", "email", "phone", "subject", "message"]
        widgets = {"message": forms.Textarea(attrs={"rows": 5})}

    def clean_website(self):
        if self.cleaned_data.get("website"):
            raise forms.ValidationError("Spam detected.")
        return ""


class QuoteForm(ContactForm):
    class Meta(ContactForm.Meta):
        fields = ["name", "company", "email", "phone", "country", "interest", "message"]
        labels = {"interest": "Product / service required", "message": "Project details (site, quantities, timelines)"}
        widgets = {"message": forms.Textarea(attrs={"rows": 6})}
