import pytest
from datetime import datetime, timedelta
from unittest.mock import patch
from server import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_book_rejects_past_competition_date(client):
    # Prepare mocked data with a past competition date
    mocked_clubs = [
        {"name": "Test Club", "email": "test@club.com", "points": "10"}
    ]
    mocked_competitions = [
        {
            "name": "Past Competition",
            "date": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S"),
            "numberOfPlaces": "10"
        }
    ]

    # Patch the global variables in server.py
    with patch("server.clubs", mocked_clubs), patch("server.competitions", mocked_competitions):
        # Make a GET request to the book route
        response = client.get("/book/Past%20Competition/Test%20Club")

        # Check that the response includes the error message and not the success one
        assert b"you cannot book places for a past competition" in response.data
        assert b"Great-booking complete!" not in response.data
