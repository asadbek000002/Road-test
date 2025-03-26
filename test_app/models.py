from django.db import models


class Category(models.Model):
    title = models.CharField(max_length=255)  # Kategoriya nomi
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Question(models.Model):
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, related_name='questions', null=True, blank=True)
    text = models.TextField()  # Savol matni
    image = models.ImageField(upload_to='questions/', null=True, blank=True)  # Savolga tegishli rasm (ixtiyoriy)
    correct_answer = models.TextField()  # To‘g‘ri javob matni

    def __str__(self):
        return self.text


class AnswerChoice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=255)  # Variant matni
    is_correct = models.BooleanField(default=False)  # To‘g‘ri yoki noto‘g‘ri ekanligi

    def __str__(self):
        return f"{self.text} ({'To‘g‘ri' if self.is_correct else 'Noto‘g‘ri'})"
