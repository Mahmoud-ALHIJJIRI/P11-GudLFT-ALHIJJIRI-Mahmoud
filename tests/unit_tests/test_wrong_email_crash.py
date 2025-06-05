import pytest
from server import app, clubs
from flask import get_flashed_messages, url_for


@pytest.fixture
def client():
    """Configures the Flask app for testing and provides a test client."""
    app.config['TESTING'] = True
    # Enables session access in tests, useful for flashed messages
    app.config['SECRET_KEY'] = 'test_secret_key'  # A secret key is needed for sessions/flashing
    with app.test_client() as client:
        # Pushes an application context so that Flask's functions like url_for, flash work.
        with app.app_context():
            yield client


# Test case for a correct email (successful login)
def test_show_summary_correct_email(client, mocker):
    """
    Tests the show_summary route with a valid email.
    Verifies successful rendering of the welcome page.
    """
    mock_clubs = [
        {"name": "Test Club", "email": "test@example.com", "points": "100"},
        {"name": "Another Club", "email": "another@example.com", "points": "50"}
    ]
    mocker.patch('server.clubs', mock_clubs)  # Mock the global clubs list

    # Simulate a POST request with a valid email
    response = client.post('/showSummary', data={'email': 'test@example.com'})

    assert response.status_code == 200

    html_content = response.data.decode('utf-8')
    assert "Welcome," in html_content


# Test case for an incorrect email (email not found)
def test_show_summary_incorrect_email(client, mocker):
    """
    Tests the show_summary route with an invalid email.
    Verifies redirection to index and a flashed message.
    """
    mock_clubs = [
        {"name": "Test Club", "email": "test@example.com", "points": "100"}
    ]
    mocker.patch('server.clubs', mock_clubs)  # Mock the global clubs list

    # Simulate a POST request with an invalid email
    response = client.post('/showSummary', data={'email': 'wrong@example.com'})

    # Assert status code is 302 Found (for redirection)
    assert response.status_code == 302

    with client.session_transaction() as sess:
        flashed_messages = sess['_flashes']
        assert flashed_messages[0][1] == "Email not found. Please try again."
