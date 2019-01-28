import csv
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import generic
from .forms import CSVUploadForm
from .models import Post


class PostIndex(generic.ListView):
    model = Post


class PostImport(generic.FormView):
    template_name = 'app/import.html'
    success_url = reverse_lazy('app:index')
    form_class = CSVUploadForm

    def form_valid(self, form):
        form.save()
        return redirect('app:index')


def post_export(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="posts.csv"'
    # HttpResponseオブジェクトはファイルっぽいオブジェクトなので、csv.writerにそのまま渡せます。
    writer = csv.writer(response)
    for post in Post.objects.all():
        writer.writerow([post.pk, post.title])
    return response
