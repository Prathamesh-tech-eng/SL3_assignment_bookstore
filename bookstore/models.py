from django.db import models

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True) 
    price = models.DecimalField(max_digits=6, decimal_places=2)
    

    def __str__(self):
        return f"{self.title} by {self.author}" 