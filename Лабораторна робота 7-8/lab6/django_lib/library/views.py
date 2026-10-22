from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from .models import Book, Loan


def book_list(request):
    books = Book.objects.select_related("author").prefetch_related("genres")
    return render(request, "library/book_list.html", {"books": books})


def book_detail(request, pk):
    book = get_object_or_404(Book.objects.select_related("author"), pk=pk)
    return render(request, "library/book_detail.html", {"book": book})


@login_required
def loan_list(request):
    loans = Loan.objects.select_related("reader", "book")
    return render(request, "library/loan_list.html", {"loans": loans})
