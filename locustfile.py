import random
from locust import HttpUser, task, between

# Define your mocked data (same as in your Flask app, or a subset)
# This data will be used by Locust to generate valid requests.
MOCKED_CLUBS = [
    {"name": "Simply Lift", "email": "john@simplylift.co", "points": "100"},
    {"name": "She Lifts", "email": "kate@shelifts.co.uk", "points": "50"},
    # Add more clubs from your clubs.json if you want to simulate more variety
]

MOCKED_COMPETITIONS = [
    {"name": "Spring Festival", "date": "2020-03-27 10:00:00", "numberOfPlaces": "25"},
    {"name": "Fall Classic", "date": "2020-10-22 13:30:00", "numberOfPlaces": "13"},
    # Add more competitions from your competitions.json
]


class WebsiteUser(HttpUser):
    # User class that does requests to the Flask website

    # Host of the system under test
    host = "http://127.0.0.1:5000"

    # Minimum and maximum time (in seconds) between two consecutive requests
    wait_time = between(1, 2.5)

    common_club = MOCKED_CLUBS[0]
    common_competition = MOCKED_COMPETITIONS[0]

    # On_start method runs once per simulated user when they "start"
    def on_start(self):

        self.client.post("/showSummary", data={"email": self.common_club["email"]})
        self.club_name = self.common_club["name"]
        self.competition_name = self.common_competition["name"]

    @task(5)  # Higher weight means more frequent
    def view_index_page(self):
        # Simulate viewing the main index page.
        self.client.get("/", name="index-Page")

    @task(2)
    def view_points_sold(self):
        self.client.get("/points-sold")

    @task(1)  # Lower weight, less frequent
    def book_and_purchase_places(self):
        # Step 1: Access the booking page
        self.client.get(f"/book/{self.competition_name}/{self.club_name}", name="/book/[competition]/[club]")
        # Step 2: Attempt to purchase places
        # Ensure the number of places is reasonable and won't always hit validation errors
        places_to_book = random.randint(1, 5)  # Book 1 to 5 places

        response = self.client.post("/purchasePlaces", data={
            "competition": self.competition_name,
            "club": self.club_name,
            "places": str(places_to_book)
        }, name="/purchasePlaces [POST]")

        # Check response for failure case.
        if "Great-booking complete!" in response.text:
            print(f"Booking failed for {self.club_name} in {self.competition_name}: {response.text[:100]}")
            # Print first 100 chars of error

    @task
    def login_with_unknown_email(self):
        # Simulate attempting to log in with an unknown email.
        self.client.post("/showSummary", data={"email": "unknown@example.com"}, name="/showSummary [unknown email]")
