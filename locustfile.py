from locust import HttpUser, task, between
import random


class GUDLFTUser(HttpUser):
    wait_time = between(1, 2)  # Simulates user think time

    def on_start(self):
        # Set a known valid email to login
        self.email = "john@simplylift.co"  # Replace with a valid email from your clubs.json
        self.club_name = "Simply Lift"     # Match the email above
        self.competition_name = "Spring Festival"  # Replace with a real competition from competitions.json

        # Step 1: POST to /showSummary to simulate login
        self.client.post(
            "/showSummary",
            data={"email": self.email}
        )

    @task
    def book_and_purchase_places(self):
        # Step 2: GET booking page
        response = self.client.get(f"/book/{self.competition_name}/{self.club_name}")
        if response.status_code != 200:
            print("Booking page failed!")
            return

        # Step 3: POST to /purchasePlaces
        places = random.randint(1, 3)  # simulate booking 1 to 3 places
        self.client.post(
            "/purchasePlaces",
            data={
                "competition": self.competition_name,
                "club": self.club_name,
                "places": places
            }
        )