import json
from flask import Flask, render_template, request, redirect, flash, url_for, session
from datetime import datetime


def loadClubs():
    with open('clubs.json') as c:
        listOfClubs = json.load(c)['clubs']
    return listOfClubs

def loadCompetitions():
    with open('competitions.json') as comps:
        listOfCompetitions = json.load(comps)['competitions']
    return listOfCompetitions


app = Flask(__name__)
app.secret_key = 'something_special'

competitions = loadCompetitions()
clubs = loadClubs()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/showSummary', methods=['POST'])
def show_summary():
    email = request.form['email']
    matched_clubs = [club for club in clubs if club['email'] == email]

    if not matched_clubs:
        flash("Email not found. Please try again.")
        return redirect(url_for('index'))

    club = matched_clubs[0]

    return render_template('welcome.html', club=club, competitions=competitions)


@app.route('/book/<competition>/<club>')
def book(competition, club):
    # Find the club and competition by name
    foundClub = next((c for c in clubs if c['name'] == club), None)
    foundCompetition = next((c for c in competitions if c['name'] == competition), None)

    # If either club or competition doesn't exist, show error and go back to welcome page
    if not foundClub or not foundCompetition:
        flash("Something went wrong — please try again.")
        return render_template('welcome.html', club=foundClub, competitions=competitions)

    try:
        # Convert competition date string to datetime object
        competition_date = datetime.strptime(foundCompetition['date'], "%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        # If date format is invalid, show error
        flash("Invalid date format in competition data.")
        return render_template('welcome.html', club=foundClub, competitions=competitions)

    # If the competition date is in the past, prevent booking
    if competition_date < datetime.now():
        flash(f"Now it's {datetime.now()} - Sorry, you cannot book places for a past competition.")
        return render_template('welcome.html', club=foundClub, competitions=competitions)

    # If everything is fine, show the booking page
    return render_template('booking.html', club=foundClub, competition=foundCompetition)


@app.route('/purchasePlaces', methods=['POST'])
def purchasePlaces():
    competition = [c for c in competitions if c['name'] == request.form['competition']][0]
    club = [c for c in clubs if c['name'] == request.form['club']][0]
    session_key = f"{club['name']}_{competition['name']}"

    placesRequired = int(request.form['places'])
    available_competition_places = int(competition['numberOfPlaces'])  # From BUG5 branch
    booked_in_session = session.get(session_key, 0)  # From HEAD (BUG2 logic)

    # --- All Validation Checks ---

    # Ensure club/competition exist (from HEAD, though IndexError might precede)
    if not competition or not club:
        flash("Club or competition not found.")
        return redirect(url_for('index'))

    # Check if places required exceed club's points (from HEAD)
    if placesRequired > int(club['points']):
        flash(f"Your Point sold is: {club['points']} points. You can't buy {placesRequired}!")
        return render_template('booking.html', club=club, competition=competition)

    # Check if total booked places for this competition exceed 12 (from HEAD)
    if booked_in_session + placesRequired > 12:
        flash("You can only book a total of 12 places per competition.")
        return render_template('booking.html', club=club, competition=competition)

    # Check if places required exceed competition's available places (from BUG5)
    if placesRequired > available_competition_places:
        flash("You can't book more than the available places!")
        return render_template('booking.html', club=club, competition=competition)

    # --- If all checks pass, proceed with booking ---

    # Update session for the 12-place limit
    session[session_key] = booked_in_session + placesRequired

    # Deduct points from club
    club['points'] = str(int(club['points']) - placesRequired)

    # Deduct places from competition (present in both branches, now consolidated)
    competition['numberOfPlaces'] = available_competition_places - placesRequired

    flash('Great-booking complete!')
    return render_template('welcome.html', club=club, competitions=competitions)


@app.route('/points-sold', methods=['GET'])
def list_club_and_points():
    """
    Display a list of all clubs and their current points.

    This route renders the 'clubs.html' template and passes the
    list of clubs from the in-memory data source. Each club's name
    and point balance is shown to provide a quick overview of standings.
    """
    return render_template('clubs.html', clubs=clubs)


@app.route('/logout')
def logout():
    return redirect(url_for('index'))
