import requests

from src.models.session import process_sessions


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

    # Process the response
    if timetable_data:
        sessions = process_sessions(timetable_data)

        print("Successfully retrieved timetable data")
        # You can process the timetable_data here as needed
        print(sessions)
    else:
        print("Failed to retrieve timetable data")


if __name__ == "__main__":
    main()
