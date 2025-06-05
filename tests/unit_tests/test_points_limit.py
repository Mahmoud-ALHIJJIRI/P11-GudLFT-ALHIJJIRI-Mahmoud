# tests/unit_tests/test_purchase_places.py

import pytest
import server
from unittest.mock import patch, MagicMock

# Define initial mock data for clubs and competitions
mocked_clubs_initial = [
    {"name": "Simply Lift", "email": "john@simplylift.co", "points": "10"},
    {"name": "She Lifts", "email": "kate@shelifts.co.uk", "points": "5"}
]

mocked_competitions_initial = [
    {"name": "Spring Festival", "date": "2020-03-27 10:00:00", "numberOfPlaces": "25"},
    {"name": "Fall Classic", "date": "2020-10-22 13:30:00", "numberOfPlaces": "13"}
]


def test_purchase_places_insufficient_points(mocker):
    # Create mutable copies of mock data for the test, as the function modifies them
    mocked_clubs = [club.copy() for club in mocked_clubs_initial]
    mocked_competitions = [comp.copy() for comp in mocked_competitions_initial]

    # Patch global variables in the server module with our mock data
    mocker.patch.object(server, 'clubs', mocked_clubs)
    mocker.patch.object(server, 'competitions', mocked_competitions)

    # Mock Flask's request object and its 'form' attribute
    mock_request = MagicMock()
    mock_request.form = {
        'competition': 'Spring Festival',
        'club': 'Simply Lift',
        'places': '15'  # Club 'Simply Lift' only has 10 points
    }
    mocker.patch('server.request', mock_request)

    # Mock Flask's flash and render_template functions
    mock_flash = mocker.patch('server.flash')
    mock_render_template = mocker.patch('server.render_template')

    # Identify the specific club and competition objects that will be affected
    club_under_test = mocked_clubs[0]
    competition_under_test = mocked_competitions[0]

    # Store initial values to assert no change after the failed purchase
    initial_club_points = int(club_under_test['points'])
    initial_competition_places = int(competition_under_test['numberOfPlaces'])
    places_required = int(mock_request.form['places'])

    # Directly call the function under test
    server.purchasePlaces()

    # Assertions for the scenario where points are insufficient:

    # 1. Verify that a flash message was displayed with the correct error
    expected_flash_message = (
        f"Your Point sold is: {initial_club_points} points. You can't buy {places_required}!"
    )
    mock_flash.assert_called_once_with(expected_flash_message)

    # 2. Verify that the 'booking.html' template was rendered
    mock_render_template.assert_called_once_with(
        'booking.html',
        club=club_under_test,
        competition=competition_under_test
    )

    # 3. Verify that the club's points and competition's places did NOT change
    assert int(club_under_test['points']) == initial_club_points
    assert int(competition_under_test['numberOfPlaces']) == initial_competition_places
