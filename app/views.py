import csv
import io
from django.db import transaction
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views import generic
from .forms import CSVUploadForm
from .models import Post


class InvalidColumnsExcepion(Exception):
    """CSVの列が足りなかったり多かったりしたらこのエラー"""
    pass


class InvalidSourceExcepion(Exception):
    """CSVの読みとり中にUnicodeDecordErrorが出たらこのエラー"""
    pass


class PostIndex(generic.ListView):
    model = Post


class PostImport(generic.FormView):
    template_name = 'app/import.html'
    success_url = reverse_lazy('app:index')
    form_class = CSVUploadForm
    number_of_columns = 2  # 列の数を定義しておく。各行の列がこれかどうかを判断する

    def save_csv(self, form):
        # csv.readerに渡すため、TextIOWrapperでテキストモードなファイルに変換
        csvfile = io.TextIOWrapper(form.cleaned_data['file'])
        reader = csv.reader(csvfile)
        i = 1  # 1行目でのUnicodeDecodeError対策。for文の初回のnextでエラーになるとiの値がない為
        try:
            # iは、現在の行番号。エラーの際に補足情報として使う
            for i, row in enumerate(reader, 1):
                # 列数が違う場合
                if len(row) != self.number_of_columns:
                    raise InvalidColumnsExcepion('{0}行目が変です。本来の列数: {1}, {0}行目の列数: {2}'.format(i, self.number_of_columns, len(row)))

                # 問題なければ、この行は保存する。(実際には、form_validのtryブロック終了後に正式に保存される)
                post, created = Post.objects.get_or_create(pk=row[0])
                post.title = row[1]
                post.save()

        except UnicodeDecodeError:
            raise InvalidSourceExcepion('{}行目でデコードに失敗しました。ファイルのエンコーディングや、正しいCSVファイルか確認ください。'.format(i))

    def form_valid(self, form):
            try:
                # CSVの100行目でエラーがおきたら、前の99行分は保存されないようにする
                with transaction.atomic():
                    self.save_csv(form)
            except (InvalidColumnsExcepion, InvalidSourceExcepion) as e:
                form.add_error('file', e)  # ビューからフォームフィールドのエラーを追加する
                return super().form_invalid(form)  # エラーがあるので、ページ表示しなおしてエラー内容見せる
            else:
                return super().form_valid(form)  # うまくいったので、リダイレクトさせる


def post_export(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="posts.csv"'
    # HttpResponseオブジェクトはファイルっぽいオブジェクトなので、csv.writerにそのまま渡せます。
    writer = csv.writer(response)
    for post in Post.objects.all():
        writer.writerow([post.pk, post.title])
    return response
