from django import forms
from .models import Publisher, Review

class PublisherForm(forms.ModelForm):
    class Meta:
        model = Publisher
        fields = "__all__"

class SearchForm(forms.Form):
    SEARCH_CHOICES = [
        ('title', 'Title'),
        ('contributor', 'Contributor'),
    ]

    search = forms.CharField(
        required=False,
        min_length=3,
        widget=forms.TextInput(attrs={'placeholder': 'Enter at least 3 characters'})
    )
    search_in = forms.ChoiceField(
        choices=SEARCH_CHOICES,
        required=True,
        initial='title'
    )

class ReviewForm(forms.ModelForm):
    rating = forms.IntegerField(min_value=0, max_value=5)

    class Meta:
        model = Review
        exclude = ['date_edited', 'book']