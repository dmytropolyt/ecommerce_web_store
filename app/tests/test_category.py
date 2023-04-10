"""
Test category app.
"""
import pytest

from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image

from category.models import Category


@pytest.mark.django_db
class TestCategory:

    def test_category_model(self):
        """Test create category instance."""
        image = Image.new('RGB', (300, 300), color='red')

        image_file = SimpleUploadedFile('red_image.png', image.tobytes(), content_type='image/png')
        category = Category.objects.create(
            name='test', slug='test', description='test description', image=image_file
        )

        assert category.name == 'test'
        assert category.slug == 'test'
        assert category.description == 'test description'
        assert category.image.name == 'categories/red_image.png'

        category.image.delete()
