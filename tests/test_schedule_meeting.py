import pytest
from flask import session
from app import app 

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'your_secret_key'
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess['logged_in'] = True
        yield client
        
def test_schedule_flow(client):
    response = client.get('/address/search_address', query_string={'query': '9201 University City Blvd'}, follow_redirects=True)
    assert response.status_code == 200

    json_data = response.get_json()
    assert any('9201 University City Boulevard' in item['street'] for item in json_data)

    response = client.post('/date-time/set-date-time?address=9201+University+City+Blvd', data={
        'date': '2025-05-01',
        'time': '14:00'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Does the following information look correct?" in response.data

    with client.session_transaction() as sess:
        assert sess['address'] == '9201 University City Blvd'
        assert sess['date'] == '2025-05-01'
        assert sess['time'] == '14:00'

    response = client.post('/confirm/confirm', data={'confirm': 'Confirm'}, follow_redirects=True)
    assert response.status_code == 200
    assert b"Meeting Scheduled" in response.data or b"Home" in response.data
