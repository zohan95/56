from django import forms
from django.core.exceptions import ValidationError
from webapp.models import Article, Comment, STATUS_ACTIVE


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        exclude = ['created_at', 'updated_at']
    tag = forms.CharField(max_length=100, required=False, label='Теги')


class CommentForm(forms.ModelForm):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fields['article'].queryset = Article.objects.filter(status=STATUS_ACTIVE)

    # article = forms.ModelChoiceField(queryset=Article.objects.filter(status=STATUS_ACTIVE), label='Статья')

    class Meta:
        model = Comment
        exclude = ['created_at', 'updated_at']


class ArticleCommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['author', 'text']


class SimpleSearchForm(forms.Form):
    search = forms.CharField(max_length=100, required=False, label='Найти')


class FullSearchForm(forms.Form):
    text = forms.CharField(max_length=100, required=False, label='Текст')
    in_title = forms.BooleanField(initial=True, required=False, label='В заголовках')
    in_text = forms.BooleanField(initial=True, required=False, label='В тексте')
    in_tags = forms.BooleanField(initial=True, required=False, label='В тегах')
    in_comment_text = forms.BooleanField(initial=False, required=False, label='В тексте комментариев')

    author = forms.CharField(max_length=100, required=False, label='Автор')
    in_articles = forms.BooleanField(initial=True, required=False, label='Статей')
    in_comments = forms.BooleanField(initial=False, required=False, label='Комментариев')

    def clean(self):
        super().clean()
        text = self.cleaned_data.get('text')
        in_title = self.cleaned_data.get('in_title')
        in_text = self.cleaned_data.get('in_text')
        in_tags = self.cleaned_data.get('in_tags')
        in_comment_text = self.cleaned_data.get('in_comment_text')
        author = self.cleaned_data['author']
        in_articles = self.cleaned_data['in_articles']
        in_comments = self.cleaned_data['in_comments']
        if text or author:
            if text:
                if not (in_title or in_text or in_tags or in_comment_text):
                    raise ValidationError(
                        'One of the checkboxes: In Title, In Text, In Tags, In Comment text should be checked.',
                        code='no_text_search_destination'
                    )

            if author:
                if not(in_articles or in_comments):
                    raise ValidationError(
                        'One of the checkboxes: In Articles, In Comments text should be checked',
                        code='no_text_search_destination'
                    )
        else:
            raise ValidationError('Text or author should be filled')
        return self.cleaned_data
