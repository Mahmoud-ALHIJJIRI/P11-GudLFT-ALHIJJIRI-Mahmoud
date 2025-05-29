import pytest
from server import app, clubs  # Import Flask app and global 'clubs' list


@pytest.fixture
def client():
    """Configures the Flask app for testing."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_list_club_and_points_with_mocked_data(client, mocker):
    """
    Tests the '/points-sold' route with mocked club data.
    Verifies that the response contains the mocked club names and points.
    """
    # Define simple mock data for clubs.
    mock_clubs_data = [
        {"name": "Real Madrid", "points": "114"},
        {"name": "Barcelona", "points": "81"}
    ]

    # Patch the 'clubs' global variable in 'server.py' with mock data.
    mocker.patch('server.clubs', mock_clubs_data)

    # Simulate GET request to the endpoint.
    response = client.get('/points-sold')

    # Assert success status code.
    assert response.status_code == 200

    # Decode HTML content.
    html_content = response.data.decode('utf-8')

    # Verify mocked club data is present in HTML.
    for club in mock_clubs_data:
        assert club['name'] in html_content
        assert club['points'] in html_content
