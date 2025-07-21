from django.db import models
from django.utils import timezone


class BaseModel(models.Model):
    """Base model containing common properties"""

    created_at = models.DateTimeField(
        help_text="The creation date of the model instance",
        db_comment="The creation date of the model instance",
        default=timezone.now,
    )
    updated_at = models.DateTimeField(
        help_text="The last updated date of the model instance",
        db_comment="The last updated date of the model instance",
        auto_now=True,
    )

    class Meta:
        abstract = True
