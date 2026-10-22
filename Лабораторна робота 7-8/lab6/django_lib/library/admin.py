from django.contrib import admin

from .models import Author, Book, Genre, Loan, Reader, ReaderProfile

admin.site.register(Author)
admin.site.register(Genre)
admin.site.register(Book)
admin.site.register(Reader)
admin.site.register(ReaderProfile)
admin.site.register(Loan)
