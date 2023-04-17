import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

# def test_transcripts_route_with_loggedin_user(client):
#     with client.session_transaction() as session:
#         session['loggedin'] = True
#         session['username'] = 'John Doe'
#         session['id'] = 1

#     response = client.get('/transcripts?msg=success')
#     assert response.status_code == 200
#     assert b'John Doe' in response.data
#     assert b'success' in response.data

# def test_transcripts_route_with_loggedout_user(client):
#     response = client.get('/transcripts')
#     assert response.status_code == 302
#     assert b'Location: http://localhost/login' in response.data
