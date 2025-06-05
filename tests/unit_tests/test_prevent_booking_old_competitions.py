import pytest
import server
from unittest.mock import patch, MagicMock
from datetime import datetime

# Define initial mock data for clubs and competitions
mocked_clubs_initial = [
    {"name": "Simply Lift", "email": "john@simplylift.co", "points": "10"},
]

mocked_competitions_initial = [
    # This competition date is in the past relative to our mocked datetime.now()
    {"name": "Old Festival", "date": "2023-01-15 10:00:00", "numberOfPlaces": "20"},
    {"name": "Future Gala", "date": "2025-12-01 19:00:00", "numberOfPlaces": "30"}
]


def test_book_past_competition(mocker):
    # Create mutable copies of mock data for the test run
    mocked_clubs = [club.copy() for club in mocked_clubs_initial]
    mocked_competitions = [comp.copy() for comp in mocked_competitions_initial]

    # Patch global variables in the server module with our test-specific data
    mocker.patch.object(server, 'clubs', mocked_clubs)
    mocker.patch.object(server, 'competitions', mocked_competitions)

    # Mock datetime.now() to simulate a date AFTER the 'Old Festival' competition
    mock_now = datetime(2024, 7, 18, 12, 00, 00)
    # Patch the datetime module within the 'server' module's context
    mocker.patch('server.datetime', autospec=True)
    server.datetime.now.return_value = mock_now
    server.datetime.strptime = datetime.strptime  # Ensure strptime still works

    # Mock Flask's flash and render_template functions
    mock_flash = mocker.patch('server.flash')
    mock_render_template = mocker.patch('server.render_template')

    # Define the parameters for the 'book' function call (for a past competition)
    competition_name_to_book = "Old Festival"
    club_name_to_book = "Simply Lift"

    # Get references to the specific club and competition in our mocked data
    club_under_test = mocked_clubs[0]  # Simply Lift
    competition_under_test = mocked_competitions[0]  # Old Festival

    # Directly call the 'book' function
    server.book(competition_name_to_book, club_name_to_book)

    # Assertions:

    # 1. Verify that a flash message was displayed for the past competition
    expected_flash_message = f"Now it's {mock_now} - Sorry, you cannot book places for a past competition."
    mock_flash.assert_called_once_with(expected_flash_message)

    # 2. Verify that the 'welcome.html' template was rendered (redirecting back)
    mock_render_template.assert_called_once_with(
        'welcome.html',
        club=club_under_test,
        competitions=mocked_competitions
    )

    # 3. Verify that the mocked clubs and competitions data were NOT modified
    # (The 'book' function should not modify data if the competition is past)
    assert mocked_clubs == [{"name": "Simply Lift", "email": "john@simplylift.co", "points": "10"}]
    assert mocked_competitions[0]['numberOfPlaces'] == "20"  # Ensure places for Old Festival unchanged
    assert mocked_competitions[1]['numberOfPlaces'] == "30"  # Ensure places for Future Gala unchanged
