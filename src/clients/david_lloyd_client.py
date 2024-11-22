from datetime import datetime, timedelta
import requests
from typing import Dict, Any, Optional
from src.core.logging_config import setup_logger
from src.services.timetable_service import get_session_by_course_and_date
from dataclasses import dataclass
from urllib.parse import urljoin

logger = setup_logger(__name__)


@dataclass
class BookingResponse:
    """Data class to structure booking-related responses"""

    success: bool
    data: Dict[str, Any]
    error_message: Optional[str] = None


class DavidLloydClient:
    def __init__(
        self,
        auth_token: str,
        base_url: str = "https://mobile-app-back.davidlloyd.co.uk",
    ):
        self.base_url = base_url
        self.auth_token = auth_token
        logger.info("Initialized DavidLloydClient")

    def _get_headers(self) -> Dict[str, str]:
        return {
            "Host": "mobile-app-back.davidlloyd.co.uk",
            "content-type": "application/json",
            "accept": "application/json, text/javascript, */*; q=0.01",
            "sec-fetch-site": "cross-site",
            "accept-language": "en-GB,en;q=0.9",
            "sec-fetch-mode": "cors",
            "origin": "null",
            "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 DLL/112.0.299",
            "x-auth-token": self.auth_token,
            "x-app-version": "dev",
            "sec-fetch-dest": "empty",
        }

    def _make_request(
        self, method: str, endpoint: str, data: Dict = None
    ) -> BookingResponse:
        """Centralized request handling method"""
        url = urljoin(self.base_url, endpoint)
        logger.info(f"Making {method} request to {url}")
        logger.debug(f"Request data: {data}")

        try:
            response = requests.request(
                method, url, headers=self._get_headers(), json=data
            )
            response.raise_for_status()
            return BookingResponse(success=True, data=response.json())
        except requests.exceptions.RequestException as e:
            error_msg = str(e)
            if hasattr(e.response, "text"):
                error_msg = f"{error_msg}: {e.response.text}"
            logger.error(f"Request failed: {error_msg}")
            return BookingResponse(success=False, data={}, error_message=error_msg)

    def hold_session(
        self,
        club_id: int,
        session_id: int,
        purchase_id: int,
        contact_id: str,
        course_id: int,
    ) -> BookingResponse:
        endpoint = f"/clubs/{club_id}/classes/sessions/{session_id}/hold"
        data = {
            "purchaseId": purchase_id,
            "contactId": contact_id,
            "courseId": course_id,
        }
        return self._make_request("POST", endpoint, data)

    def get_purchase_id(self, club_id: int) -> int:
        response = self._make_request("POST", "/purchases", {"siteId": club_id})
        if not response.success:
            raise ValueError(f"Failed to get purchase ID: {response.error_message}")

        purchase_id = response.data.get("purchaseId")
        if not purchase_id:
            raise ValueError("No purchaseId found in response")
        return purchase_id

    def confirm_purchase(self, purchase_id: int) -> Dict[str, Any]:
        """Confirm the purchase after holding a session."""
        url = f"{self.base_url}/purchases/{purchase_id}/adyen-drop-in"
        logger.info(f"Confirming purchase {purchase_id}")

        data = {
            "locale": "en-gb",
            "revenueStream": "CLASS",
            "promotionsHaveBeenApplied": False,
        }

        try:
            response = requests.post(url, headers=self._get_headers(), json=data)
            response.raise_for_status()
            logger.info(
                f"Successfully confirmed purchase. Status code: {response.status_code}"
            )
            logger.debug(f"Confirmation response: {response.json()}")
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error confirming purchase: {str(e)}")
            if hasattr(e.response, "text"):
                logger.error(f"Error response: {e.response.text}")
            raise

    def get_session_id(self, course_id: int, club_id: int) -> int:
        # Calculate target date (9 days from today)
        target_date = datetime.now() + timedelta(days=9)
        session = get_session_by_course_and_date(club_id, course_id, target_date)

        if not session:
            raise ValueError(f"No session found for date {target_date}")
        return session.courseInstanceId
