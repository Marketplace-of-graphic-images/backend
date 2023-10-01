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
    """

    tags = filters.AllValuesMultipleFilter(field_name='tags__name')
    category = filters.CharFilter(method='filter_category',)

    class Meta:
        model = Image
        fields = ('tags', 'category')

    def filter_category(self, queryset, _, value):
        """
        Filters the given `queryset` based on the `value` parameter.
        """

        if value in REGAX_PATTERNS:
            return queryset.filter(image__regex=REGAX_PATTERNS.get(value))
        return queryset
