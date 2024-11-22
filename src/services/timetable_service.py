import requests
from datetime import datetime

from src.models.session import (
    Session,
    SessionCollection,
)


def get_club_timetable(club_id: int) -> dict | None:
    url = f"https://mobile-app-back.davidlloyd.co.uk/clubs/{club_id}/sessions/timetable"

    try:
        response = requests.get(url)

        response.raise_for_status()

        return response.json()

    except requests.RequestException as e:
        print(f"Error making request: {e}")
        return None


def get_session_by_course_and_date(
    club_id: int, course_id: int, date: datetime
) -> Session | None:
    timetable_data = get_club_timetable(club_id)
    if timetable_data:
        collection = SessionCollection(timetable_data)
        return collection.find_session_by_course_and_date(course_id, date)
    return None
