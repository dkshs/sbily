from django.db import models


class DeletedShortenedLinkQuerySet(models.QuerySet):
    def restore(self):
        for obj in self:
            obj.restore()


class DeletedShortenedLinkManager(models.Manager):
    def get_queryset(self) -> DeletedShortenedLinkQuerySet:
        return DeletedShortenedLinkQuerySet(self.model, using=self._db)
