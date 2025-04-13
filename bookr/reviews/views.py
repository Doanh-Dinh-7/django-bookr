from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from .models import Book, Review, Contributor, Publisher
from .utils import average_rating
from django.urls import reverse
from .forms import PublisherForm, SearchForm, ReviewForm
from django.utils.timezone import now
from django.contrib import messages

# Create your views here.
def index(request):
    return render(request, 'base.html')

def search(request):
    query = request.GET.get('search', '')
    return render(request, 'base.html', {'query': query})

def welcome_view(request):
    # message = f'<html><h1>Welcome to Bookr!</h1><p>{Book.objects.count()} books and counting!</p></html>'
    # return HttpResponse(message)
    return render(request, 'base.html')

def book_list(request):
    books = Book.objects.all()
    book_list = []
    for book in books:
        reviews = book.review_set.all()
        if reviews:
            book_rating = average_rating([review.rating for
                                          review in reviews])
            number_of_reviews = len(reviews)
        else:
            book_rating = None
            number_of_reviews = 0
        book_list.append({'book': book,
                          'book_rating': book_rating,
                          'number_of_reviews':
                           number_of_reviews})

    context = {
        'book_list': book_list
    }
    return render(request, 'reviews/book_list.html', context)

def book_detail(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    reviews = Review.objects.filter(book=book)

    return render(request, 'reviews/book_detail.html', {
        'book': book,
        'book_rating': average_rating([review.rating for review in reviews]),
        'reviews': reviews
    })

def publisher_edit(request, pk=None):
    if pk is not None:
        publisher = get_object_or_404(Publisher, pk=pk)
    else:
        publisher = None


    if request.method == 'POST':
        form = PublisherForm(request.POST, instance=publisher)
        if form.is_valid():
            updated_publisher = form.save()
            if publisher is None:
                messages.success(request, "Publisher '{}' was created.".format(updated_publisher))
            else:
                messages.success(request, "Publisher '{}' was updated.".format(updated_publisher))
            return redirect("publisher_edit",updated_publisher.pk)
    else:
        form = PublisherForm(instance=publisher)
    # return render(request, "form-example.html", {"method": request.method, "form": form})
    context = {
        "form": form,
        "instance": publisher,
        "model_type": "Publisher",
    }
    return render(request, "reviews/instance-form.html", context)

def book_search(request):
    form = SearchForm(request.GET)
    books = []
    search_text = ''

    if form.is_valid():
        search_text = form.cleaned_data.get('search', '')
        search_in = form.cleaned_data.get('search_in', 'title')

        if search_text:
            if search_in == 'title':
                books = Book.objects.filter(title__icontains=search_text)
            else:  # Tìm kiếm theo contributor
                contributors = Contributor.objects.filter(
                    first_names__icontains=search_text
                ) | Contributor.objects.filter(last_names__icontains=search_text)

                books = set()
                for contributor in contributors:
                    books.update(contributor.book_set.all())

    return render(request, 'reviews/search_results.html', {'form': form, 'books': books, 'search_text': search_text})

def review_edit(request, book_pk, review_pk=None):
    book = get_object_or_404(Book, pk=book_pk)
    review = get_object_or_404(Review, pk=review_pk, book=book) if review_pk else None

    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            review = form.save(commit=False)
            review.book = book
            if review_pk:
                review.date_edited = now()
            review.save()
            messages.success(request, f'Review for "{book.title} ({book.isbn})" created' if not review_pk else f'Review for "{book.title} ({book.isbn})" updated')
            return redirect(reverse('book_detail', kwargs={'book_id': book.pk}))
    else:
        form = ReviewForm(instance=review)

    return render(request, 'reviews/instance-form.html', {
        'form': form,
        'instance': review,
        'model_type': 'Review',
        'related_model_type': 'Book',
        'related_instance': book
    })