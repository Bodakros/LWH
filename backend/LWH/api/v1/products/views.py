from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Q
from django.db.models import Max
from ..utils.image_services import validate_image, process_image, get_image_metadata, generate_thumbnails

from .models import (
    ProductCategory, TaxType, TaxRate, Product, ProductImage,
    Attribute, AttributeOption, ProductAttributeValue,
    ProductMultipleAttributeValue
)
from .serializers import (
    ProductCategorySerializer, ProductCategoryListSerializer,
    TaxTypeSerializer, TaxRateSerializer, AttributeSerializer, AttributeOptionSerializer,
    ProductListSerializer, ProductSerializer, ProductImageSerializer,
    ProductAttributeValueSerializer, ProductMultipleAttributeValueSerializer
)


# API для категорій продуктів
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def product_category_list(request):
    """
    Отримання списку категорій продуктів або створення нової категорії.
    """
    if request.method == 'GET':
        # Отримуємо тільки кореневі категорії (без parent)
        root_categories = ProductCategory.objects.filter(parent__isnull=True)
        serializer = ProductCategorySerializer(root_categories, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = ProductCategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticatedOrReadOnly])
def product_category_detail(request, pk):
    """
    Отримання, оновлення або видалення категорії продуктів.
    """
    category = get_object_or_404(ProductCategory, pk=pk)

    if request.method == 'GET':
        serializer = ProductCategorySerializer(category)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = ProductCategorySerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# API для типів податків
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def tax_type_list(request):
    """
    Отримання списку типів податків або створення нового типу податку.
    """
    if request.method == 'GET':
        tax_types = TaxType.objects.all()
        serializer = TaxTypeSerializer(tax_types, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        # Перевірка дозволів (можливо, тільки для адміністраторів)
        if not request.user.is_staff:
            return Response(
                {"detail": "Ви не маєте дозволу створювати типи податків."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = TaxTypeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticatedOrReadOnly])
def tax_type_detail(request, pk):
    """
    Отримання, оновлення або видалення типу податку.
    """
    tax_type = get_object_or_404(TaxType, pk=pk)

    if request.method == 'GET':
        serializer = TaxTypeSerializer(tax_type)
        return Response(serializer.data)

    elif request.method == 'PUT':
        # Перевірка дозволів (можливо, тільки для адміністраторів)
        if not request.user.is_staff:
            return Response(
                {"detail": "Ви не маєте дозволу оновлювати типи податків."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = TaxTypeSerializer(tax_type, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        # Перевірка дозволів (можливо, тільки для адміністраторів)
        if not request.user.is_staff:
            return Response(
                {"detail": "Ви не маєте дозволу видаляти типи податків."},
                status=status.HTTP_403_FORBIDDEN
            )

        tax_type.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# API для податкових ставок
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def tax_rate_list(request):
    """
    Отримання списку податкових ставок або створення нової ставки.
    """
    if request.method == 'GET':
        # Додаємо фільтрацію за типом податку
        tax_type_id = request.query_params.get('tax_type')

        tax_rates = TaxRate.objects.all()

        if tax_type_id:
            tax_rates = tax_rates.filter(tax_type_id=tax_type_id)

        serializer = TaxRateSerializer(tax_rates, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        # Перевірка дозволів (можливо, тільки для адміністраторів)
        if not request.user.is_staff:
            return Response(
                {"detail": "Ви не маєте дозволу створювати податкові ставки."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = TaxRateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticatedOrReadOnly])
def tax_rate_detail(request, pk):
    """
    Отримання, оновлення або видалення податкової ставки.
    """
    tax_rate = get_object_or_404(TaxRate, pk=pk)

    if request.method == 'GET':
        serializer = TaxRateSerializer(tax_rate)
        return Response(serializer.data)

    elif request.method == 'PUT':
        # Перевірка дозволів (можливо, тільки для адміністраторів)
        if not request.user.is_staff:
            return Response(
                {"detail": "Ви не маєте дозволу оновлювати податкові ставки."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = TaxRateSerializer(tax_rate, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        # Перевірка дозволів (можливо, тільки для адміністраторів)
        if not request.user.is_staff:
            return Response(
                {"detail": "Ви не маєте дозволу видаляти податкові ставки."},
                status=status.HTTP_403_FORBIDDEN
            )

        tax_rate.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# API для атрибутів продуктів
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def attribute_list(request):
    """
    Отримання списку атрибутів продуктів або створення нового атрибуту.
    """
    if request.method == 'GET':
        attributes = Attribute.objects.all()
        serializer = AttributeSerializer(attributes, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = AttributeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticatedOrReadOnly])
def attribute_detail(request, pk):
    """
    Отримання, оновлення або видалення атрибуту продукту.
    """
    attribute = get_object_or_404(Attribute, pk=pk)

    if request.method == 'GET':
        serializer = AttributeSerializer(attribute)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = AttributeSerializer(attribute, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        attribute.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def attribute_option_list(request, attribute_id):
    """
    Отримання списку варіантів значень атрибуту або створення нового варіанту.
    """
    attribute = get_object_or_404(Attribute, pk=attribute_id)

    if request.method == 'GET':
        options = attribute.options.all()
        serializer = AttributeOptionSerializer(options, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = AttributeOptionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(attribute=attribute)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticatedOrReadOnly])
def attribute_option_detail(request, attribute_id, pk):
    """
    Отримання, оновлення або видалення варіанту значення атрибуту.
    """
    attribute = get_object_or_404(Attribute, pk=attribute_id)
    option = get_object_or_404(AttributeOption, pk=pk, attribute=attribute)

    if request.method == 'GET':
        serializer = AttributeOptionSerializer(option)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = AttributeOptionSerializer(option, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        option.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# API для продуктів
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def product_list(request):
    """
    Отримання списку продуктів або створення нового продукту.
    """
    if request.method == 'GET':
        # Фільтрація за категорією, продавцем, типом продукту
        category_id = request.query_params.get('category')
        seller_id = request.query_params.get('seller')
        product_type = request.query_params.get('type')
        search_query = request.query_params.get('search')

        products = Product.objects.all()

        if category_id:
            # Включаємо продукти з підкатегорій
            category_ids = [int(category_id)]
            child_categories = ProductCategory.objects.filter(parent_id=category_id)
            category_ids.extend(child.id for child in child_categories)
            products = products.filter(category_id__in=category_ids)

        if seller_id:
            products = products.filter(seller_id=seller_id)

        if product_type:
            products = products.filter(product_type=product_type)

        if search_query:
            products = products.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(sku__icontains=search_query)
            )

        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        # Тільки продавці можуть створювати продукти
        if not request.user.is_seller:
            return Response(
                {"detail": "Тільки продавці можуть створювати продукти."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(seller=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticatedOrReadOnly])
def product_detail(request, pk):
    """
    Отримання, оновлення або видалення продукту.
    """
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'GET':
        serializer = ProductSerializer(product, context={'request': request})
        return Response(serializer.data)

    elif request.method == 'PUT':
        # Перевіряємо, чи користувач є власником продукту
        if product.seller != request.user:
            return Response(
                {"detail": "Ви не маєте дозволу редагувати цей продукт."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = ProductSerializer(product, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        # Перевіряємо, чи користувач є власником продукту
        if product.seller != request.user:
            return Response(
                {"detail": "Ви не маєте дозволу видаляти цей продукт."},
                status=status.HTTP_403_FORBIDDEN
            )

        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def calculate_product_taxes(request, pk):
    """
    Розрахунок податків для конкретного продукту.
    """
    product = get_object_or_404(Product, pk=pk)

    # Отримання параметрів запиту
    quantity = request.query_params.get('quantity', 1)
    try:
        quantity = int(quantity)
    except (ValueError, TypeError):
        quantity = 1

    include_breakdown = request.query_params.get('breakdown', 'true').lower() == 'true'

    # Розрахунок податків
    if include_breakdown:
        taxes = product.calculate_taxes(quantity=quantity)
        total_tax = sum(taxes.values())
        base_price = product.base_price * quantity
        final_price = base_price + total_tax

        return Response({
            'product_id': product.id,
            'product_name': product.name,
            'base_price': product.base_price,
            'quantity': quantity,
            'base_total': base_price,
            'tax_breakdown': taxes,
            'total_tax_amount': total_tax,
            'final_price': final_price
        })
    else:
        total_tax = product.calculate_total_tax_amount(quantity=quantity)
        base_price = product.base_price * quantity
        final_price = base_price + total_tax

        return Response({
            'product_id': product.id,
            'product_name': product.name,
            'base_price': product.base_price,
            'quantity': quantity,
            'base_total': base_price,
            'total_tax_amount': total_tax,
            'final_price': final_price
        })


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
@parser_classes([MultiPartParser, FormParser])
def product_image_list(request, product_id):
    """
    Отримання списку зображень продукту або додавання нового зображення.
    """
    product = get_object_or_404(Product, pk=product_id)

    if request.method == 'GET':
        images = product.images.all().order_by('order', '-created_at')
        serializer = ProductImageSerializer(images, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        # Check if user is the product seller
        if product.seller != request.user:
            return Response(
                {"detail": "You don't have permission to add images to this product."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Get image file from request
        image_file = request.FILES.get('image')
        if not image_file:
            return Response(
                {"detail": "No image file provided."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate image
        is_valid, error_message = validate_image(
            image_file,
            max_size=10 * 1024 * 1024,  # 10MB
            formats=['.jpg', '.jpeg', '.png', '.gif', '.webp']
        )
        if not is_valid:
            return Response(
                {"detail": error_message},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Process image
        processed_image = process_image(
            image_file,
            quality=85,
            max_width=2000,
            max_height=2000
        )

        # Get image metadata
        metadata = get_image_metadata(image_file)

        # Create a new serializer instance with processed file
        serializer_data = request.data.copy()
        serializer_data['image'] = processed_image

        serializer = ProductImageSerializer(data=serializer_data)
        if serializer.is_valid():
            # Add additional data
            serializer.validated_data['product'] = product

            # Determine if this is the main image (if first image or is_main=True)
            is_main = product.images.count() == 0 or request.data.get('is_main') == 'true'
            serializer.validated_data['is_main'] = is_main

            # Set order if not provided
            if 'order' not in serializer.validated_data:
                # Get the max order value and add 1
                max_order = product.images.aggregate(Max('order'))['order__max'] or 0
                serializer.validated_data['order'] = max_order + 1

            # Save image
            image = serializer.save()

            # Generate thumbnails
            thumbnails = generate_thumbnails(
                image_file,
                image.image.name,
                sizes={
                    'small': (150, 150),
                    'medium': (300, 300),
                    'large': (600, 600)
                }
            )

            # Return response with metadata
            response_data = serializer.data
            response_data['thumbnails'] = thumbnails
            response_data['metadata'] = metadata

            return Response(response_data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticatedOrReadOnly])
@parser_classes([MultiPartParser, FormParser])
def product_image_detail(request, product_id, pk):
    """
    Отримання, оновлення або видалення зображення продукту.
    """
    product = get_object_or_404(Product, pk=product_id)
    image = get_object_or_404(ProductImage, pk=pk, product=product)

    if request.method == 'GET':
        serializer = ProductImageSerializer(image)

        # Add metadata to response
        response_data = serializer.data
        response_data['metadata'] = get_image_metadata(image.image)

        return Response(response_data)

    elif request.method == 'PUT':
        # Check permissions
        if product.seller != request.user:
            return Response(
                {"detail": "You don't have permission to edit this product's images."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Handle image file update if provided
        image_file = request.FILES.get('image')
        if image_file:
            # Validate image
            is_valid, error_message = validate_image(
                image_file,
                max_size=10 * 1024 * 1024,  # 10MB
                formats=['.jpg', '.jpeg', '.png', '.gif', '.webp']
            )
            if not is_valid:
                return Response(
                    {"detail": error_message},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Process image
            processed_image = process_image(
                image_file,
                quality=85,
                max_width=2000,
                max_height=2000
            )

            # Update serializer data with processed file
            serializer_data = request.data.copy()
            serializer_data['image'] = processed_image
        else:
            serializer_data = request.data

        serializer = ProductImageSerializer(image, data=serializer_data, partial=True)
        if serializer.is_valid():
            # Handle is_main flag
            if 'is_main' in request.data and request.data.get('is_main') == 'true':
                serializer.validated_data['is_main'] = True

            # Save updated image
            updated_image = serializer.save()

            # Return response with metadata
            response_data = serializer.data
            response_data['metadata'] = get_image_metadata(updated_image.image)

            return Response(response_data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        # Check permissions
        if product.seller != request.user:
            return Response(
                {"detail": "You don't have permission to delete this product's images."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Check if it's the main image and if there are other images
        if image.is_main and product.images.count() > 1:
            # Find another image to set as main
            new_main = product.images.exclude(pk=image.pk).first()
            if new_main:
                new_main.is_main = True
                new_main.save()

        # Delete the image
        image.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def product_attribute_list(request, product_id):
    """
    Отримання списку значень атрибутів продукту або додавання нового значення.
    """
    product = get_object_or_404(Product, pk=product_id)

    if request.method == 'GET':
        attribute_values = product.attribute_values.all()
        serializer = ProductAttributeValueSerializer(attribute_values, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        # Перевіряємо, чи користувач є власником продукту
        if product.seller != request.user:
            return Response(
                {"detail": "Ви не маєте дозволу додавати атрибути до цього продукту."},
                status=status.HTTP_403_FORBIDDEN
            )

        attribute_id = request.data.get('attribute')
        if not attribute_id:
            return Response(
                {"detail": "Необхідно вказати атрибут."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Перевіряємо, чи існує значення атрибуту для цього продукту
        try:
            attribute_value = ProductAttributeValue.objects.get(
                product=product,
                attribute_id=attribute_id
            )
            # Якщо існує, оновлюємо його
            serializer = ProductAttributeValueSerializer(attribute_value, data=request.data)
        except ProductAttributeValue.DoesNotExist:
            # Якщо не існує, створюємо новий
            serializer = ProductAttributeValueSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(product=product)

            # Для атрибутів типу MULTIPLE_SELECT обробляємо список значень
            if 'multiple_option_ids' in request.data:
                attribute = Attribute.objects.get(pk=attribute_id)
                if attribute.attribute_type == Attribute.MULTIPLE_SELECT:
                    # Видаляємо всі поточні значення
                    ProductMultipleAttributeValue.objects.filter(
                        product_attribute=serializer.instance
                    ).delete()

                    # Додаємо нові значення
                    for option_id in request.data.get('multiple_option_ids', []):
                        try:
                            option = AttributeOption.objects.get(pk=option_id, attribute=attribute)
                            ProductMultipleAttributeValue.objects.create(
                                product_attribute=serializer.instance,
                                attribute_option=option
                            )
                        except AttributeOption.DoesNotExist:
                            pass

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticatedOrReadOnly])
def product_attribute_detail(request, product_id, pk):
    """
    Отримання, оновлення або видалення значення атрибуту продукту.
    """
    product = get_object_or_404(Product, pk=product_id)
    attribute_value = get_object_or_404(ProductAttributeValue, pk=pk, product=product)

    if request.method == 'GET':
        serializer = ProductAttributeValueSerializer(attribute_value)
        return Response(serializer.data)

    elif request.method == 'PUT':
        # Перевіряємо, чи користувач є власником продукту
        if product.seller != request.user:
            return Response(
                {"detail": "Ви не маєте дозволу редагувати атрибути цього продукту."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = ProductAttributeValueSerializer(attribute_value, data=request.data)
        if serializer.is_valid():
            serializer.save()

            # Для атрибутів типу MULTIPLE_SELECT обробляємо список значень
            if 'multiple_option_ids' in request.data:
                attribute = attribute_value.attribute
                if attribute.attribute_type == Attribute.MULTIPLE_SELECT:
                    # Видаляємо всі поточні значення
                    ProductMultipleAttributeValue.objects.filter(
                        product_attribute=attribute_value
                    ).delete()

                    # Додаємо нові значення
                    for option_id in request.data.get('multiple_option_ids', []):
                        try:
                            option = AttributeOption.objects.get(pk=option_id, attribute=attribute)
                            ProductMultipleAttributeValue.objects.create(
                                product_attribute=attribute_value,
                                attribute_option=option
                            )
                        except AttributeOption.DoesNotExist:
                            pass

            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        # Перевіряємо, чи користувач є власником продукту
        if product.seller != request.user:
            return Response(
                {"detail": "Ви не маєте дозволу видаляти атрибути цього продукту."},
                status=status.HTTP_403_FORBIDDEN
            )

        attribute_value.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reorder_product_images(request, product_id):
    """
    Reorder product images.
    """
    product = get_object_or_404(Product, pk=product_id)

    # Check permissions
    if product.seller != request.user:
        return Response(
            {"detail": "You don't have permission to reorder this product's images."},
            status=status.HTTP_403_FORBIDDEN
        )

    # Get image_id to order mapping from request
    image_orders = request.data.get('image_orders', [])
    if not image_orders or not isinstance(image_orders, list):
        return Response(
            {"detail": "Invalid data format. Expected a list of {image_id: order} objects."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Update order for each image
    updated_images = []
    for item in image_orders:
        try:
            image_id = item.get('image_id')
            new_order = item.get('order')

            if not image_id or new_order is None:
                continue

            image = ProductImage.objects.get(pk=image_id, product=product)
            image.order = new_order
            image.save(update_fields=['order'])
            updated_images.append(image_id)
        except ProductImage.DoesNotExist:
            pass

    return Response({
        "detail": f"Successfully reordered {len(updated_images)} images.",
        "updated_images": updated_images
    })
