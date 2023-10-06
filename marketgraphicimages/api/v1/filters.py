from django.db.models import Q
from django_filters.rest_framework import FilterSet, filters

from images.models import Image

REGAX_PATTERNS = {
    'raster_image': r'\.(png|jpe?g|webp)$',
    'vector_image': r'\.(eps)$',
    'gif_image': r'\.(gif)$',
}


class ImageFilter(FilterSet):
    """
    Filter for images.

    Parameters:
    - Filter by tags.
    - Filter by category based on format of image.
    - FIlter by name. Double filtering: by entering the beginning of the name,
    by entering an arbitrary place.
    """

    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
    category = filters.CharFilter(method='filter_category',)
    name = filters.CharFilter(method='filter_name',)

    class Meta:
        model = Image
        fields = ('tags', 'category', 'name',)

    def filter_category(self, queryset, _, value):
        """
        Filters the given `queryset` based on the `value` parameter.
        """

        if value in REGAX_PATTERNS:
            return queryset.filter(image__regex=REGAX_PATTERNS.get(value))
        return queryset

    def filter_name(self, queryset, _, value):
        """
        Filters the specified `queryset` of queries based on the match with
        the beginning of the name, then by a match anywhere in the name.
        """
        return queryset.filter(Q(name__icontains=value) | Q(
            name__startswith=value)).distinct()
