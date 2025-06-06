import pytest
import server
from unittest.mock import MagicMock

# Define initial mock data for clubs and competitions
mocked_clubs_initial = [
    {"name": "Simply Lift", "email": "john@simplylift.co", "points": "100"},
    {"name": "She Lifts", "email": "kate@shelifts.co.uk", "points": "50"}
]

mocked_competitions_initial = [
    {"name": "Spring Festival", "date": "2020-03-27 10:00:00", "numberOfPlaces": "25"},
    {"name": "Fall Classic", "date": "2020-10-22 13:30:00", "numberOfPlaces": "13"}
]


def test_purchase_places_points_reflected(mocker):
    # Create mutable copies of mock data for the test run
    mocked_clubs = [club.copy() for club in mocked_clubs_initial]
    mocked_competitions = [comp.copy() for comp in mocked_competitions_initial]

    # Patch global variables in the server module with our test-specific data
    mocker.patch.object(server, 'clubs', mocked_clubs)
    mocker.patch.object(server, 'competitions', mocked_competitions)

    # Mock Flask's request object to simulate a successful form submission
    mock_request = MagicMock()
    mock_request.form = {
        'competition': 'Spring Festival',
        'club': 'Simply Lift',
        'places': '10'  # Buying 10 places
    }
    mocker.patch('server.request', mock_request)

    # --- ADDED: Mock Flask's session object ---
    mock_session = MagicMock()
    # For a successful booking, assume no previous bookings (or less than 12)
    mock_session.get.return_value = 0  # Simulate 0 places booked previously
    mocker.patch('server.session', mock_session)
    # ----------------------------------------

    # Mock Flask's flash and render_template functions
    mock_flash = mocker.patch('server.flash')
    mock_render_template = mocker.patch('server.render_template')

    # Get references to the specific club and competition in our mocked data
    club_under_test = mocked_clubs[0]  # Simply Lift
    competition_under_test = mocked_competitions[0]  # Spring Festival

    # Store initial values to assert changes after the successful purchase
    initial_club_points = int(club_under_test['points'])
    initial_competition_places = int(competition_under_test['numberOfPlaces'])
    places_to_buy = int(mock_request.form['places'])

    # Calculate expected session_key
    expected_session_key = f"{club_under_test['name']}_{competition_under_test['name']}"

    # Directly call the 'purchasePlaces' function
    server.purchasePlaces()

    # Assertions:

    # 1. Verify session.get was called to check previous bookings
    mock_session.get.assert_called_once_with(expected_session_key, 0)

    # 2. Verify session was updated with the new booking amount
    mock_session.__setitem__.assert_called_once_with(expected_session_key, places_to_buy)

    # 3. Verify that the success flash message was displayed
    mock_flash.assert_called_once_with('Great-booking complete!')

    # 4. Verify that the 'welcome.html' template was rendered
    mock_render_template.assert_called_once_with(
        'welcome.html',
        club=club_under_test,
        competitions=mocked_competitions
    )

    # 5. Verify that the club's points were correctly reduced
    expected_club_points = initial_club_points - places_to_buy
    assert int(club_under_test['points']) == expected_club_points

    # 6. Verify that the competition's number of places was correctly reduced
    expected_competition_places = initial_competition_places - places_to_buy
    assert int(competition_under_test['numberOfPlaces']) == expected_competition_places
