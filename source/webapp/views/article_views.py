from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils.http import urlencode
from django.views.generic import ListView, DetailView, CreateView,\
    UpdateView, DeleteView

from webapp.forms import ArticleForm, ArticleCommentForm, SimpleSearchForm
from webapp.models import Article, STATUS_ARCHIVED, STATUS_ACTIVE
from django.core.paginator import Paginator
from webapp.models import Tag


class IndexView(ListView):
    template_name = 'article/index.html'
    context_object_name = 'articles'
    model = Article
    ordering = ['-created_at']
    paginate_by = 5
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
        paginator = Paginator(comments, 3, 0)
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
        list_tags = form.cleaned_data['tags'].split(',')
        form.cleaned_data.pop('tags')
        tags = self.new_tags(list_tags)
        self.object = form.save()
        self.object.tags.add(*tags)
        self.object.save()
        return super().form_valid(form)

    def new_tags(self, tags):
        tags_list = []
        for i in tags:
            if i:
                Tag.objects.get_or_create(name=i)
                tags_list.append(Tag.objects.get(name=i))
        return tags_list


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
