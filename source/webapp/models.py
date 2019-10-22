from django.db import models


STATUS_ACTIVE = 'active'
STATUS_ARCHIVED = 'archived'
ARTICLE_STATUSES = (
    (STATUS_ACTIVE, 'Active'),
    (STATUS_ARCHIVED, 'Archived')
)


class Article(models.Model):
    title = models.CharField(max_length=200, null=False, blank=False, verbose_name='Заголовок')
    text = models.TextField(max_length=3000, null=False, blank=False, verbose_name='Текст')
    author = models.CharField(max_length=40, null=False, blank=False, default='Unknown', verbose_name='Автор')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Время создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Время изменения')
    category = models.ForeignKey('Category', on_delete=models.PROTECT, null=True, blank=True, verbose_name='Категория',
                                 related_name='articles')
    tags = models.ManyToManyField('webapp.Tag', related_name='articles', blank=True, verbose_name='Теги')
    status = models.CharField(max_length=20, default=STATUS_ACTIVE, choices=ARTICLE_STATUSES, verbose_name='Статус')

    def __str__(self):
        return self.title

    @property
    def is_active(self):
        return self.status == STATUS_ACTIVE

    @property
    def is_archived(self):
        return self.status == STATUS_ARCHIVED


class Comment(models.Model):
    article = models.ForeignKey('webapp.Article', related_name='comments',
                                on_delete=models.CASCADE, verbose_name='Статья')
    text = models.TextField(max_length=400, verbose_name='Комментарий')
    author = models.CharField(max_length=40, null=True, blank=True, default='Аноним', verbose_name='Автор')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Время создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Время изменения')

    def __str__(self):
        return self.text[:20]


class Category(models.Model):
    name = models.CharField(max_length=20, verbose_name='Название')

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=31, verbose_name='Тег')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Время создания')

    def __str__(self):
        return self.name
