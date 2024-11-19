import requests
from datetime import datetime, timedelta

from src.models.session import format_session, process_sessions, SessionCollection


def get_club_timetable(club_id=42):
    # Base URL
    url = f"https://mobile-app-back.davidlloyd.co.uk/clubs/{club_id}/sessions/timetable"

    try:
        # Make the GET request
        response = requests.get(url)

        # Raise an exception for bad status codes
        response.raise_for_status()

        # Return JSON response if successful
        return response.json()

    except requests.RequestException as e:
        print(f"Error making request: {e}")
        return None


def main():
    # Get the timetable data
    timetable_data = get_club_timetable()

    if timetable_data:
        # Create SessionCollection instance directly
        collection = SessionCollection(timetable_data)

        # Calculate target date (9 days from today)
        target_date = datetime.now() + timedelta(days=9)

        # Find specific session (example with course_id=123)
        session = collection.find_session_by_course_and_date(101786949, target_date)

        if session:
            print(f"Found session: {format_session(session)}")
        else:
            print("No matching session found")
    else:
        print("Failed to retrieve timetable data")


if __name__ == "__main__":
    main()
