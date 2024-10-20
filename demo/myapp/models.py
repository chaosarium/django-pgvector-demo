from django.db import models
from pgvector.django import VectorField


class Record(models.Model):
    text = models.TextField()
    vector = VectorField(dimensions=3)

    def __str__(self):
        return self.text
