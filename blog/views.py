import random
from django.views.generic import ListView, DetailView
from blog.models import Article


class ArticleListView(ListView):
    model = Article
    paginate_by = 2

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(is_published=True)
        return queryset


class ArticleDetailView(DetailView):
    model = Article

    def get_object(self, queryset=None):
        self.object = super().get_object()
        self.object.views_count += 1
        self.object.save()
        return self.object

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        article_list = list(Article.objects.filter(is_published=True))
        qty = 2 if len(article_list) >= 2 else len(article_list)
        context_data['object_list'] = random.sample(article_list, qty)
        return context_data