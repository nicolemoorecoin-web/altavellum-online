from django import forms

# Display labels and amount rules per plan
PLAN_RULES = {
    "starter":  {"label": "Starter Plan",  "min": 1000,  "max": 4999},
    "premium":  {"label": "Premium Plan",  "min": 5000,  "max": 29000},
    "business": {"label": "Business Plan", "min": 30000, "max": 1000000},
}

class ContactForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        label="Name",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Name"}),
    )
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "Email"}),
    )
    subject = forms.CharField(
        max_length=100,
        label="Subject",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Subject"}),
    )
    message = forms.CharField(
        label="Create a message here",
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "placeholder": "Create a message here",
                "rows": 7,
                "cols": 30,
            }
        ),
    )


class StartInvestmentForm(forms.Form):
    plan = forms.ChoiceField(
        choices=[(k, v["label"]) for k, v in PLAN_RULES.items()],
        widget=forms.HiddenInput(),
    )
    amount = forms.DecimalField(
        min_value=1,
        decimal_places=2,
        max_digits=12,
        widget=forms.NumberInput(
            attrs={"class": "uk-input", "placeholder": "Enter amount"}
        ),
    )

    def __init__(self, plan_key, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if plan_key not in PLAN_RULES:
            raise ValueError("Invalid plan key")
        self.plan_key = plan_key
        rules = PLAN_RULES[plan_key]
        self.fields["plan"].initial = plan_key
        self.fields["amount"].min_value = rules["min"]
        self.fields["amount"].max_value = rules["max"]

    def clean_amount(self):
        amt = self.cleaned_data["amount"]
        rules = PLAN_RULES[self.plan_key]
        if not (rules["min"] <= float(amt) <= rules["max"]):
            raise forms.ValidationError(
                f"Amount must be between ${rules['min']:,} and ${rules['max']:,}."
            )
        return amt
