from dataclasses import dataclass, field
from typing import List, Optional, Callable
from datetime import datetime


@dataclass
class Session:
    courseId: int
    courseInstanceId: int
    courseTemplateId: int
    courseGroupId: int
    siteId: int
    date: str
    startTime: str
    duration: int
    name: str
    classSport: str
    classTypeId: int
    level: str
    levelTranslationKey: str
    locations: List[str]
    standardPrice: float
    currency: Optional[str]
    isPartOfACourse: bool
    isJunior: bool
    isSenior: bool
    isClubEvent: bool
    minAge: int
    maxAge: int
    instructorNames: List[str]
    status: str
    oneClickBookingUrl: Optional[str]
    lastModified: str
    usesStations: bool
    currentCourseOccupancy: Optional[int]
    maxCourseOccupancy: Optional[int]
    courseBookingReference: Optional[str]
    courseLocationIds: Optional[List[str]]
    isAllStars: bool
    standardPriceDecimal: float
    instancesForBooking: List[str]

    def get_start_datetime(self) -> datetime:
        return datetime.strptime(f"{self.date} {self.startTime}", "%Y-%m-%d %H:%M")

    def is_virtual(self) -> bool:
        return any(
            instructor.lower() == "virtual" for instructor in self.instructorNames
        )

    def get_age_range(self) -> str:
        if self.maxAge == -1:
            return f"{self.minAge}+"
        return f"{self.minAge}-{self.maxAge}"


class SessionCollection:
    def __init__(self, sessions_data: dict):
        # Remove description field when creating Session objects
        sessions = []
        for session_data in sessions_data["sessionsDetails"]:
            session_data.pop("description", None)  # Remove description
            session_data.pop("liveStreamDetails", None)  # Remove liveStreamDetails
            sessions.append(Session(**session_data))
        self.sessions = sessions

    def filter(self, **kwargs) -> List[Session]:
        """Filter sessions based on multiple criteria"""
        filtered_sessions = self.sessions

        for key, value in kwargs.items():
            filtered_sessions = [
                session
                for session in filtered_sessions
                if getattr(session, key) == value
            ]

        return filtered_sessions

    def filter_custom(self, filter_func: Callable[[Session], bool]) -> List[Session]:
        """Filter sessions using a custom filter function"""
        return [session for session in self.sessions if filter_func(session)]

    def get_adult_sessions(self) -> List[Session]:
        """Get all non-junior sessions"""
        return self.filter(isJunior=False)

    def find_session_by_course_and_date(
        self, course_id: int, target_date: datetime
    ) -> Optional[Session]:
        """Find a session by course ID and specific date"""
        target_date_str = target_date.strftime("%Y-%m-%d")

        matching_sessions = [
            session
            for session in self.sessions
            if session.courseId == course_id and session.date == target_date_str
        ]

        return matching_sessions[0] if matching_sessions else None


def format_session(session: Session) -> dict:
    """Convert a session to a simplified dictionary format"""
    return {
        "id": session.courseInstanceId,
        "courseInstanceId": session.courseInstanceId,
        "name": session.name,
        "time": session.startTime,
        "date": session.date,
        "duration": session.duration,
        "location": ", ".join(session.locations),
        "instructor": ", ".join(session.instructorNames),
        "age_range": session.get_age_range(),
        "is_virtual": session.is_virtual(),
    }


# Example usage
def process_sessions(json_data: dict) -> List[dict]:
    """Process sessions and return simplified data"""
    collection = SessionCollection(json_data)

    # Get adult sessions only
    adult_sessions = collection.get_adult_sessions()

    # Format the sessions into simplified dictionaries
    formatted_sessions = [format_session(session) for session in adult_sessions]

    # Sort by date first, then time
    formatted_sessions.sort(key=lambda x: (x["date"], x["time"]))

    return formatted_sessions
