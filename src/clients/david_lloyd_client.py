from datetime import datetime, timedelta
import requests
from typing import Dict, Any
from src.core.logging_config import setup_logger
from src.services.timetable_service import get_session_by_course_and_date

logger = setup_logger(__name__)


class DavidLloydClient:
    def __init__(self, auth_token: str):
        self.base_url = "https://mobile-app-back.davidlloyd.co.uk"
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

    def hold_session(
        self,
        club_id: int,
        session_id: int,
        purchase_id: int,
        contact_id: str,
        course_id: int,
    ) -> Dict[str, Any]:
        url = f"{self.base_url}/clubs/{club_id}/classes/sessions/{session_id}/hold"
        logger.info(f"Making hold_session request to {url}")

        data = {
            "purchaseId": purchase_id,
            "contactId": contact_id,
            "courseId": course_id,
        }
        logger.debug(f"Request data: {data}")

        try:
            response = requests.post(url, headers=self._get_headers(), json=data)
            response.raise_for_status()
            logger.info(
                f"Successfully held session. Status code: {response.status_code}"
            )
            logger.debug(f"Response data: {response.json()}")
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error holding session: {str(e)}")
            if hasattr(e.response, "text"):
                logger.error(f"Error response: {e.response.text}")
            raise

    def get_purchase_id(self, club_id: int) -> int:
        """Get a valid purchase ID for booking classes."""
        url = f"{self.base_url}/purchases"
        logger.info(f"Getting purchase ID for club {club_id}")

        data = {"siteId": club_id}

        try:
            response = requests.post(url, headers=self._get_headers(), json=data)
            response.raise_for_status()
            response_data = response.json()

            logger.info("Successfully retrieved purchase data")
            logger.debug(f"Purchase response: {response_data}")

            # Extract purchaseId from the response
            if purchase_id := response_data.get("purchaseId"):
                logger.info(f"Found purchase ID: {purchase_id}")
                return purchase_id
            else:
                logger.error("No purchaseId found in response")
                raise ValueError("No purchaseId found in response")

        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting purchase ID: {str(e)}")
            if hasattr(e.response, "text"):
                logger.error(f"Error response: {e.response.text}")
            raise

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