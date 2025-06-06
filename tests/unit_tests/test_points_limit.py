import pytest
import server
from unittest.mock import MagicMock

mocked_clubs_initial = [
    {"name": "Simply Lift", "email": "john@simplylift.co", "points": "10"},
    {"name": "She Lifts", "email": "kate@shelifts.co.uk", "points": "5"}
]

mocked_competitions_initial = [
    {"name": "Spring Festival", "date": "2020-03-27 10:00:00", "numberOfPlaces": "25"},
    {"name": "Fall Classic", "date": "2020-10-22 13:30:00", "numberOfPlaces": "13"}
]


def test_purchase_places_insufficient_points(mocker):
    mocked_clubs = [club.copy() for club in mocked_clubs_initial]
    mocked_competitions = [comp.copy() for comp in mocked_competitions_initial]

    mocker.patch.object(server, 'clubs', mocked_clubs)
    mocker.patch.object(server, 'competitions', mocked_competitions)

    mock_request = MagicMock()
    mock_request.form = {
        'competition': 'Spring Festival',
        'club': 'Simply Lift',
        'places': '15'  # Trying to buy 15 places, but Simply Lift only has 10 points
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
    places_required = int(mock_request.form['places'])

    server.purchasePlaces()

    expected_flash_message = (
        f"Your Point sold is: {initial_club_points} points. You can't buy {places_required}!"
    )
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
