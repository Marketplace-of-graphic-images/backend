from django_filters.rest_framework import FilterSet, filters, CharFilter

from images.models import Image


class ImageFilter(FilterSet):
    tags = filters.AllValuesMultipleFilter(field_name='tags__name')
    formats = CharFilter(field_name='format',)
    licenses = CharFilter(field_name='license',)

    class Meta:
        model = Image
        fields = ('format', 'license', 'tags',)
