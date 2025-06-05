import pytest
import server
from unittest.mock import MagicMock

# Define initial mock data for clubs and competitions
mocked_clubs_initial = [
    {"name": "Simply Lift", "email": "john@simplylift.co", "points": "100"},
    {"name": "She Lifts", "email": "kate@shelifts.co.uk", "points": "50"}
]

mocked_competitions_initial = [
    # Set numberOfPlaces low for this test case
    {"name": "Small Competition", "date": "2025-09-01 10:00:00", "numberOfPlaces": "5"},
    {"name": "Large Event", "date": "2025-10-22 13:30:00", "numberOfPlaces": "50"}
]


def test_purchase_places_exceeds_competition_capacity(mocker):
    # Create mutable copies of mock data for the test run
    mocked_clubs = [club.copy() for club in mocked_clubs_initial]
    mocked_competitions = [comp.copy() for comp in mocked_competitions_initial]

    # Patch global variables in the server module with our test-specific data
    mocker.patch.object(server, 'clubs', mocked_clubs)
    mocker.patch.object(server, 'competitions', mocked_competitions)

    # Mock Flask's request object to simulate form submission
    mock_request = MagicMock()
    mock_request.form = {
        'competition': 'Small Competition',
        'club': 'Simply Lift',
        'places': '8'  # Trying to book 8 places, but only 5 are available
    }
    mocker.patch('server.request', mock_request)

    # Mock Flask's flash and render_template functions
    mock_flash = mocker.patch('server.flash')
    mock_render_template = mocker.patch('server.render_template')

    # Get references to the specific club and competition in our mocked data
    club_under_test = mocked_clubs[0]  # Simply Lift
    competition_under_test = mocked_competitions[0]  # Small Competition

    # Store initial states to verify no changes occur after a rejected purchase
    initial_club_points = int(club_under_test['points'])
    initial_competition_places = int(competition_under_test['numberOfPlaces'])
    places_to_buy = int(mock_request.form['places'])
    available_places = initial_competition_places  # Available places before attempt

    # Directly call the 'purchasePlaces' function
    server.purchasePlaces()

    # Assertions:

    # 1. Verify the correct error message was flashed
    expected_flash_message = "You can't book more than the available places!"
    mock_flash.assert_called_once_with(expected_flash_message)

    # 2. Verify that the user was returned to the booking page
    mock_render_template.assert_called_once_with(
        'booking.html',
        club=club_under_test,
        competition=competition_under_test
    )

    # 3. Verify that club points and competition places remained unchanged
    assert int(club_under_test['points']) == initial_club_points
    assert int(competition_under_test['numberOfPlaces']) == initial_competition_places
