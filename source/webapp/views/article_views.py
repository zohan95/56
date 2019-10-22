from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils.http import urlencode
from django.views.generic import ListView, DetailView, CreateView, \
    UpdateView, DeleteView, FormView

from webapp.forms import ArticleForm, ArticleCommentForm, SimpleSearchForm
from webapp.models import Article, STATUS_ARCHIVED, STATUS_ACTIVE
from django.core.paginator import Paginator
from webapp.models import Tag

from webapp.forms import FullSearchForm


class IndexView(ListView):
    template_name = 'article/index.html'
    context_object_name = 'articles'
    model = Article
    ordering = ['-created_at']
    paginate_by = 3
    paginate_orphans = 1

    def get(self, request, *args, **kwargs):
        self.form = self.get_search_form()
        self.search_value = self.get_search_value()
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset().filter(status=STATUS_ACTIVE)
        if self.search_value:
            queryset = queryset.filter(
                Q(title__icontains=self.search_value)
                | Q(author__icontains=self.search_value)
                | Q(tags__name__iexact=self.search_value)
            )
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['form'] = self.form
        if self.search_value:
            context['query'] = urlencode({'search': self.search_value})
        context['archived_articles'] = self.get_archived_articles()
        return context

    def get_archived_articles(self):
        queryset = super().get_queryset().filter(status=STATUS_ARCHIVED)
        return queryset

    def get_search_form(self):
        return SimpleSearchForm(data=self.request.GET)

    def get_search_value(self):
        if self.form.is_valid():
            return self.form.cleaned_data['search']
        return None


class ArticleView(DetailView):
    template_name = 'article/article.html'
    model = Article

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        article = self.object
        context['form'] = ArticleCommentForm()
        comments = article.comments.order_by('-created_at')
        self.paginate_comments_to_context(comments, context)
        return context

    def paginate_comments_to_context(self, comments, context):
        paginator = Paginator(comments, 5, 0)
        page_number = self.request.GET.get('page', 1)
        page = paginator.get_page(page_number)
        context['paginator'] = paginator
        context['page_obj'] = page
        context['comments'] = page.object_list
        context['is_paginated'] = page.has_other_pages()


class ArticleCreateView(CreateView):
    form_class = ArticleForm
    model = Article
    template_name = 'article/create.html'

    def get_success_url(self):
        return reverse('article_view', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        list_new_tags = form.cleaned_data['tag'].split(',')
        list_new_tags = self.new_tags(list_new_tags)
        for i in list_new_tags:
            form.cleaned_data['tags'] = form.cleaned_data['tags'] | i
        return super().form_valid(form)

    def new_tags(self, tags):
        list_tags = []
        for i in tags:
            if i:
                Tag.objects.get_or_create(name=i)
                list_tags.append(Tag.objects.filter(name=i))
        return list_tags


class ArticleUpdateView(UpdateView):
    model = Article
    template_name = 'article/update.html'
    form_class = ArticleForm
    context_object_name = 'article'

    def get_success_url(self):
        return reverse('article_view', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        list_new_tags = form.cleaned_data['tag'].split(',')
        list_new_tags = self.new_tags(list_new_tags)
        for i in list_new_tags:
            form.cleaned_data['tags'] = form.cleaned_data['tags'] | i
        return super().form_valid(form)

    def new_tags(self, tags):
        list_tags = []
        for i in tags:
            if i:
                Tag.objects.get_or_create(name=i)
                list_tags.append(Tag.objects.filter(name=i))
        return list_tags


class ArticleDeleteView(DeleteView):
    model = Article
    template_name = 'article/delete.html'
    context_object_name = 'article'
    success_url = reverse_lazy('index')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.status = STATUS_ARCHIVED
        self.object.save()
        return redirect(self.get_success_url())


class TagView(ListView):
    template_name = 'article/index.html'
    context_object_name = 'articles'
    model = Article
    ordering = ['-created_at']
    paginate_by = 5
    paginate_orphans = 1
    tag = ''

    def get(self, request, *args, **kwargs):
        self.form = self.get_search_form()
        self.tag = kwargs.get('tag')
        print(self.tag)
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset().filter(status=STATUS_ACTIVE)
        queryset = queryset.filter(
            Q(tags__name__iexact=self.tag))
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['form'] = self.form
        context['query'] = urlencode({'tag': self.tag})
        return context

    def get_search_form(self):
        return SimpleSearchForm(data=self.request.GET)


class ArticleSearchView(FormView):
    template_name = 'article/search.html'
    form_class = FullSearchForm
    art = None

    def form_valid(self, form, *args, **kwargs):
        text = form.cleaned_data.get('text')
        author = form.cleaned_data.get('author')
        query = self.get_text_search_query(form, text, author)
        context = self.get_context_data(form=form)
        self.art = Article.objects.filter(query).distinct().order_by('-created_at')
        self.get_context_data()
        context['articles'] = self.art
        return self.render_to_response(context=context)

    def get_text_search_query(self, form, text, author):
        query = Q()
        query2 = Q()
        if text:
            in_title = form.cleaned_data.get('in_title')
            if in_title:
                query = query | Q(title__icontains=text)
            in_text = form.cleaned_data.get('in_text')
            if in_text:
                query = query | Q(text__icontains=text)
            in_tags = form.cleaned_data.get('in_tags')
            if in_tags:
                query = query | Q(tags__name__iexact=text)
            in_comment_text = form.cleaned_data.get('in_comment_text')
            if in_comment_text:
                query = query | Q(comments__text__icontains=text)
        if author:
            in_articles = form.cleaned_data['in_articles']
            in_comments = form.cleaned_data['in_comments']
            if in_articles:
                query2 = query2 | Q(comments__author__iexact=author)
            if in_comments:
                query2 = query2 | Q(author__iexact=author)
        return query & query2


