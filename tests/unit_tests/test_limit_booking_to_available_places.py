import pytest
import server
from unittest.mock import MagicMock

mocked_clubs_initial = [
    {"name": "Simply Lift", "email": "john@simplylift.co", "points": "100"},
    {"name": "She Lifts", "email": "kate@shelifts.co.uk", "points": "50"}
]

mocked_competitions_initial = [
    {"name": "Small Competition", "date": "2025-09-01 10:00:00", "numberOfPlaces": "5"},
    {"name": "Large Event", "date": "2025-10-22 13:30:00", "numberOfPlaces": "50"}
]


def test_purchase_places_exceeds_competition_capacity(mocker):
    mocked_clubs = [club.copy() for club in mocked_clubs_initial]
    mocked_competitions = [comp.copy() for comp in mocked_competitions_initial]

    mocker.patch.object(server, 'clubs', mocked_clubs)
    mocker.patch.object(server, 'competitions', mocked_competitions)

    mock_request = MagicMock()
    mock_request.form = {
        'competition': 'Small Competition',
        'club': 'Simply Lift',
        'places': '8'  # Trying to book 8 places, but only 5 are available
    }
    mocker.patch('server.request', mock_request)

    mock_session = MagicMock()
    mock_session.get.return_value = 0  # Assume 0 places booked previously, doesn't matter for this test
    mocker.patch('server.session', mock_session)

    # --- ADDED: Mock redirect and url_for for full coverage ---
    mock_redirect = mocker.patch('server.redirect', return_value='redirect_mock')
    mock_url_for = mocker.patch('server.url_for', return_value='/mock_url')
    # -----------------------------------------------------------

    mock_flash = mocker.patch('server.flash')
    mock_render_template = mocker.patch('server.render_template')

    club_under_test = mocked_clubs[0]
    competition_under_test = mocked_competitions[0]

    initial_club_points = int(club_under_test['points'])
    initial_competition_places = int(competition_under_test['numberOfPlaces'])

    server.purchasePlaces()

    expected_flash_message = "You can't book more than the available places!"
    mock_flash.assert_called_once_with(expected_flash_message)

    mock_render_template.assert_called_once_with(
        'booking.html',
        club=club_under_test,
        competition=competition_under_test
    )

    assert int(club_under_test['points']) == initial_club_points
    assert int(competition_under_test['numberOfPlaces']) == initial_competition_places
    mock_session.__setitem__.assert_not_called()
    # Verify redirect/url_for were NOT called in this path
    mock_redirect.assert_not_called()
    mock_url_for.assert_not_called()
