from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Product, Order, Category

User = get_user_model()

class AuthenticationTests(APITestCase):
    def setUp(self):
        self.user_data = {'email': 'testuser@example.com', 'password': 'testpassword'}
        self.user = User.objects.create_user(**self.user_data)

    def test_register_user(self):
        url = reverse('register')
        data = {'email': 'newuser@example.com', 'password': 'newpassword'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_login_user(self):
        url = reverse('login')
        response = self.client.post(url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

    def test_logout_user(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('logout')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class ProductTests(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(email='admin@example.com', password='adminpass')
        self.client.force_authenticate(user=self.admin_user)
        self.category = Category.objects.create(name='Dairy')
        self.product_data = {
            'name': 'Milk', 'description': 'Fresh milk', 'price': 50.00, 'category': self.category.id
        }

    def test_create_product(self):
        url = reverse('product-list')
        response = self.client.post(url, self.product_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_products(self):
        Product.objects.create(**self.product_data)
        url = reverse('product-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_update_product(self):
        product = Product.objects.create(**self.product_data)
        url = reverse('product-detail', args=[product.id])
        new_data = {'name': 'Updated Milk', 'price': 55.00}
        response = self.client.patch(url, new_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated Milk')

    def test_delete_product(self):
        product = Product.objects.create(**self.product_data)
        url = reverse('product-detail', args=[product.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

class OrderTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='user@example.com', password='password')
        self.client.force_authenticate(user=self.user)
        self.category = Category.objects.create(name='Snacks')
        self.product = Product.objects.create(name='Cookies', description='Chocolate cookies', price=100.00, category=self.category)
        self.order_data = {'product': self.product.id, 'quantity': 2}

    def test_create_order(self):
        url = reverse('order-list')
        response = self.client.post(url, self.order_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_orders(self):
        Order.objects.create(user=self.user, product=self.product, quantity=2)
        url = reverse('order-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_update_order_status(self):
        order = Order.objects.create(user=self.user, product=self.product, quantity=2)
        url = reverse('order-detail', args=[order.id])
        response = self.client.patch(url, {'status': 'Shipped'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'Shipped')
