from django.db import models

class Page(models.Model):
    url = models.URLField(unique=True)
    title = models.CharField(max_length=300, blank=True)
    content = models.TextField()
    rank = models.FloatField(default=0.0)
    crawled_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title or self.url


class Index(models.Model):
    page = models.ForeignKey(Page, related_name='indexes', on_delete=models.CASCADE)
    keyword = models.CharField(max_length=200)
    position = models.IntegerField()

    def __str__(self):
        return f"{self.keyword} - {self.page.title}"
    