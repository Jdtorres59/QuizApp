from django.db import models


class Quiz(models.Model):
    title = models.CharField(max_length=200, blank=True)
    input_text = models.TextField(blank=True)
    output_json = models.TextField(blank=True)
    output_text = models.TextField(blank=True)
    question_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title or f"Quiz {self.pk}"
