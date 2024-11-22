from src.clients.david_lloyd_client import DavidLloydClient
from src.core.auth import OktaAuth
from src.core.logging_config import setup_logger

logger = setup_logger(__name__)


def main():
    logger.info("Starting main function")
    # Get auth token using OktaAuth
    try:
        okta_auth = OktaAuth()
        auth_token = okta_auth.get_valid_token()
        logger.info("Successfully obtained auth token")
    except Exception as e:
        logger.error(f"Failed to get auth token: {str(e)}")
        raise

    client = DavidLloydClient(auth_token)

    try:
        # Constants
        club_id = 42
        course_id = 101786949  # tennis advanced
        contact_id = "Ve+lBmwwMU6FcU46j2ZEcg"

        # Get the session_id for the course 9 days ahead
        session_id = client.get_session_id(course_id, club_id)
        logger.info(f"Found session_id: {session_id}")
        if not session_id:
            raise ValueError(f"No session found for course_id {course_id}")

        # Get purchase ID
        purchase_id = client.get_purchase_id(club_id)

        client.hold_session(
            club_id=club_id,
            session_id=session_id,
            purchase_id=purchase_id,
            contact_id=contact_id,
            course_id=course_id,
        )
        logger.info("Successfully held session")

        # Confirm the purchase
        confirm_response = client.confirm_purchase(purchase_id)
        logger.info("Successfully confirmed purchase")
        logger.debug(f"Final confirmation response: {confirm_response}")

        return confirm_response
    except Exception as e:
        logger.error(f"Error in main function: {str(e)}")
        raise


if __name__ == "__main__":
    main()
