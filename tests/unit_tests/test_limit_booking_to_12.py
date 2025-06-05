import pytest
import server
from unittest.mock import MagicMock

# Define initial mock data for clubs and competitions
# Ensure clubs have enough points so that point limit doesn't interfere with this test
mocked_clubs_initial = [
    {"name": "Simply Lift", "email": "john@simplylift.co", "points": "100"},
    {"name": "She Lifts", "email": "kate@shelifts.co.uk", "points": "50"}
]

mocked_competitions_initial = [
    {"name": "Spring Festival", "date": "2020-03-27 10:00:00", "numberOfPlaces": "25"},
    {"name": "Fall Classic", "date": "2020-10-22 13:30:00", "numberOfPlaces": "13"}
]


def test_purchase_places_exceeds_max_per_competition(mocker):
    # Create mutable copies of mock data for the test run
    mocked_clubs = [club.copy() for club in mocked_clubs_initial]
    mocked_competitions = [comp.copy() for comp in mocked_competitions_initial]

    # Patch global variables in the server module with our test-specific data
    mocker.patch.object(server, 'clubs', mocked_clubs)
    mocker.patch.object(server, 'competitions', mocked_competitions)

    # Mock Flask's request object to simulate form submission
    mock_request = MagicMock()
    mock_request.form = {
        'competition': 'Spring Festival',
        'club': 'Simply Lift',
        'places': '8'  # Club has already booked 5, trying to book 8 more (total 13 > 12)
    }
    mocker.patch('server.request', mock_request)

    # Mock Flask's session object to control previously booked places
    mock_session = MagicMock()
    # Simulate that 'Simply Lift' has already booked 5 places for 'Spring Festival'
    mock_session.get.return_value = 5
    mocker.patch('server.session', mock_session)

    # Mock Flask's flash and render_template functions to assert their calls
    mock_flash = mocker.patch('server.flash')
    mock_render_template = mocker.patch('server.render_template')

    # Get references to the specific club and competition in our mocked data
    club_under_test = mocked_clubs[0]  # Simply Lift
    competition_under_test = mocked_competitions[0]  # Spring Festival

    # Store initial states to verify no changes occur after a rejected purchase
    initial_club_points = int(club_under_test['points'])
    initial_competition_places = int(competition_under_test['numberOfPlaces'])

    # Directly call the 'purchasePlaces' function
    server.purchasePlaces()

    # Assertions:

    # 1. Verify that session.get was called to check previous bookings
    expected_session_key = f"{club_under_test['name']}_{competition_under_test['name']}"
    mock_session.get.assert_called_once_with(expected_session_key, 0)

    # 2. Verify the correct error message was flashed
    expected_flash_message = "You can only book a total of 12 places per competition."
    mock_flash.assert_called_once_with(expected_flash_message)

    # 3. Verify that the user was returned to the booking page
    mock_render_template.assert_called_once_with(
        'booking.html',
        club=club_under_test,
        competition=competition_under_test
    )

    # 4. Verify that club points and competition places remained unchanged
    assert int(club_under_test['points']) == initial_club_points
    assert int(competition_under_test['numberOfPlaces']) == initial_competition_places

    # 5. Verify that the session was NOT updated for the failed booking
    mock_session.__setitem__.assert_not_called()
