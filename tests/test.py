from app import app


class TestViews:

    def setup(self):
        app.testing = True
        self.client = app.test_client()

    def test_index_route(self):
        response = self.client.get('/')
        assert response.status_code == 200

    def test_admin_route(self):
        response = self.client.get('/admin/')
        assert response.status_code == 200

    def test_user_route(self):
        response = self.client.get('/admin/users/')
        assert response.status_code == 302

    def test_product_route(self):
        response = self.client.get('/admin/product/')
        assert response.status_code == 302

    def test_order_route(self):
        response = self.client.get('/admin/order/')
        assert response.status_code == 302

    def test_address_model_view(self):
        response = self.client.get('/admin/address/')
        assert response.status_code == 302
