from django_filters.rest_framework import FilterSet, filters

from images.models import Image


class ImageFilter(FilterSet):
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')

    class Meta:
        model = Image
        fields = ('tags',)
