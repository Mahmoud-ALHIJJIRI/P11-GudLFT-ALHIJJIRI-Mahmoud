import server
import pytest

mocked_clubs = [
    {"name": "Simply Lift", "email": "john@simplylift.co", "points": "13"},
    {"name": "She Lifts", "email": "kate@shelifts.co.uk", "points": "13"}
]
mocked_competitions = [
    {"name": "Spring Festival", "date": "2020-03-27 10:00:00", "numberOfPlaces": "25"},
    {"name": "Fall Classic", "date": "2020-10-22 13:30:00", "numberOfPlaces": "13"}
]


@pytest.fixture
def client():
    server.app.config['TESTING'] = True
    server.app.config['SECRET_KEY'] = 'dfs'
    with server.app.test_client() as client:
        yield client


def test_limit_booking_to_12(client, mocker):
    """Tests the scenario where a club attempts to purchase more than 12 places."""
    mocker.patch('server.loadClubs', return_value=mocked_clubs)
    mocker.patch('server.loadCompetitions', return_value=mocked_competitions)

    server.clubs = server.loadClubs()
    server.competitions = server.loadCompetitions()
    # Define the data that will be sent with the POST request
    form_data = {
        'club': 'Simply Lift',
        'competition': 'Spring Festival',
        'places': '13'  # Attempting to buy 13 places.
    }
    # Simulate a POST request to the /purchasePlaces route
    response = client.post('/purchasePlaces', data=form_data)
    # Assertions:
    # 1. Verify that club points and competition places remain unchanged
    #    because the purchase should have been blocked.
    assert server.clubs[0]['points'] == "13"  # Points should still be 13
    assert server.competitions[0]['numberOfPlaces'] == "25"  # Places should still be 25
    # 2. Check that the correct template is rendered (booking.html)
    assert b"Booking" in response.data
