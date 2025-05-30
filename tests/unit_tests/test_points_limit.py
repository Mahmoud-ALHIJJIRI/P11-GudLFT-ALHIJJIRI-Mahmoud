import pytest
import server

mocked_clubs = [
    {"name": "Simply Lift", "email": "john@simplylift.co", "points": "5"},
    {"name": "She Lifts", "email": "kate@shelifts.co.uk", "points": "12"}
]
mocked_competitions = [
    {"name": "Spring Festival", "date": "2020-03-27 10:00:00", "numberOfPlaces": "25"},
    {"name": "Fall Classic", "date": "2020-10-22 13:30:00", "numberOfPlaces": "13"}
]


@pytest.fixture
def client():
    server.app.config['TESTING'] = True
    # The secret key is needed for session management (like flash messages)
    server.app.config['SECRET_KEY'] = 'something_special'
    with server.app.test_client() as client:
        yield client


def test_purchase_places_insufficient_points(client, mocker):
    """
    Tests the scenario where a club attempts to purchase more places
    than their available points allow.
    """
    mocker.patch('server.loadClubs', return_value=mocked_clubs)
    mocker.patch('server.loadCompetitions', return_value=mocked_competitions)

    server.clubs = server.loadClubs()
    server.competitions = server.loadCompetitions()
    # Define the data that will be sent with the POST request
    form_data = {
        'club': 'Simply Lift',
        'competition': 'Spring Festival',
        'places': '10'  # Attempting to buy 10 places with only 5 points
    }
    # Simulate a POST request to the /purchasePlaces route
    response = client.post('/purchasePlaces', data=form_data)
    # Assertions:
    # 1. Verify that club points and competition places remain unchanged
    #    because the purchase should have been blocked.
    assert server.clubs[0]['points'] == "5"  # Points should still be 5
    assert server.competitions[0]['numberOfPlaces'] == "25"  # Places should still be 25
    # 2. Check that the correct template is rendered (booking.html)
    assert b"Booking" in response.data


def test_purchase_places_sufficient_points(client, mocker):
    """Tests the scenario where a club successfully purchases places,
    ensuring points and places are correctly updated."""
    mocker.patch('server.loadClubs', return_value=mocked_clubs)
    mocker.patch('server.loadCompetitions', return_value=mocked_competitions)

    server.clubs = server.loadClubs()
    server.competitions = server.loadCompetitions()
    # Define the data that will be sent with the POST request
    form_data = {
        'club': 'Simply Lift',
        'competition': 'Spring Festival',
        'places': '3'  # Attempting to buy 10 places with only 5 points
    }
    # Simulate a POST request to the /purchasePlaces route
    response = client.post('/purchasePlaces', data=form_data)
    # Assertions:
    # 1. Verify that club points and competition places has changed
    #    because the purchase should have been done.
    assert server.clubs[0]['points'] == "2"  # Should remain only 2 Points
    assert server.competitions[0]['numberOfPlaces'] == 22  # Places should be decreased to 15
    # 2. Check that the correct template is rendered (booking.html)
    assert b"Welcome" in response.data
