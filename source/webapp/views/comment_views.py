from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import CreateView, ListView, \
    UpdateView, DeleteView

from webapp.forms import CommentForm, ArticleCommentForm
from webapp.models import Comment, Article, STATUS_ACTIVE


class CommentListView(ListView):
    template_name = 'comment/list.html'
    model = Comment
    context_object_name = 'comments'
    ordering = ['-created_at']
    paginate_by = 10
    paginate_orphans = 3


class CommentForArticleCreateView(CreateView):
    model = Comment
    template_name = 'comment/create.html'
    form_class = ArticleCommentForm

    def dispatch(self, request, *args, **kwargs):
        self.article = self.get_article()
        if self.article.is_archived:
            raise Http404
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        self.article.comments.create(**form.cleaned_data)
        return redirect('article_view', pk=self.article.pk)

    def get_article(self):
        article_pk = self.kwargs.get('pk')
        return get_object_or_404(Article, pk=article_pk)


class CommentCreateView(CreateView):
    model = Comment
    template_name = 'comment/create.html'
    form_class = CommentForm

    # def get_form(self, form_class=None):
    #     form = super().get_form(form_class)
    #     form.fields['article'].queryset = Article.objects.filter(status=STATUS_ACTIVE)
    #     return form

    def get_success_url(self):
        return reverse('article_view', kwargs={'pk': self.object.article.pk})


class CommentUpdateView(UpdateView):
    model = Comment
    template_name = 'comment/update.html'
    form_class = ArticleCommentForm
    context_object_name = 'comment'

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.article.is_archived:
            raise Http404
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('article_view', kwargs={'pk': self.object.article.pk})


class CommentDeleteView(DeleteView):
    model = Comment

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.article.is_archived:
            raise Http404
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('article_view', kwargs={'pk': self.object.article.pk})
