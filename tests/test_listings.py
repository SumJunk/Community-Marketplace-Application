import unittest
from app import app
from flask import session

class ListingsTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

        with app.app_context():
            with self.app.session_transaction() as sess:
                sess['logged_in'] = True
                sess['user_id'] = 1

    def test_get_create_listing_page(self):
        response = self.app.get('/create-listing')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Create Listing', response.data)

    def test_create_listing_post(self):
        data = {
            'title': 'Awesome chair',
            'price': '10',
            'category': 'furniture',
            'description': 'A chair that is awesome.'
        }
        with open('tests/test_image.jpg', 'rb') as img:
            data['image'] = (img, 'test_image.jpg')
            response = self.app.post('/create-listing', data=data, content_type='multipart/form-data')
        
        self.assertEqual(response.status_code, 201)
        self.assertIn(b'Listing created successfully', response.data)

    def test_my_listings_page(self):
        response = self.app.get('/my-listings')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'My Listings', response.data)

if __name__ == '__main__':
    unittest.main()