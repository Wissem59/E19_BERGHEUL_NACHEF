from django.conf import settings
from django.db import models
from django.utils.timezone import now


class Section(models.Model):
    url = models.CharField(max_length=255, unique=True)   
    name = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.name

    @property
    def favorites_count(self):
        # Count how many users have favorited this section
        return self.favorite_sections.count()


class Favorite_section(models.Model):
    # Reference the custom user model
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # Reference the `Section` model via `url`
    section_url = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='favorite_sections')
    added_on = models.DateTimeField(default=now)

    class Meta:
        unique_together = ('user', 'section_url')  # Ensure unique relationships

    def __str__(self):
        return f'{self.user.username} - {self.section_url.name}'
