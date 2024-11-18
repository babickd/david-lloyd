import requests
from datetime import datetime, timedelta


class OktaAuth:
    def __init__(self):
        self.auth_url = "https://davidlloyd.okta.com/api/v1/authn"
        self.authorize_url = (
            "https://digitalmanager.davidlloyd.co.uk/oauth2/default/v1/authorize"
        )
        self.token_url = (
            "https://digitalmanager.davidlloyd.co.uk/oauth2/default/v1/token"
        )
        self.client_id = "0oa3n4dj2s9UuXIRt417"
        self.redirect_uri = "uk.co.davidlloyd.mobile-app:/login"
        self.access_token = None
        self.refresh_token = None
        self.token_expiry = None

    def authenticate(self):
        payload = {
            "username": "+447876260006",
            "password": "vuwmy2-vijwic-bexcuB",
            "options": {
                "multiOptionalFactorEnroll": True,
                "warnBeforePasswordExpired": True,
            },
        }
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Python-Script/1.0",
        }

        response = requests.post(self.auth_url, json=payload, headers=headers)

        if response.status_code == 200:
            auth_response = response.json()
            session_token = auth_response.get("sessionToken")
            if session_token:
                return self.get_tokens(session_token)

        raise Exception(f"Authentication failed: {response.status_code}")

    def get_tokens(self, session_token):
        params = {
            "sessionToken": session_token,
            "response_type": "code",
            "code_challenge_method": "S256",
            "scope": "openid profile offline_access",
            "code_challenge": "w84zQww0CRKtrH6_MhwR__KOqnhIFslQR_xw5DGMCac",
            "redirect_uri": self.redirect_uri,
            "client_id": self.client_id,
            "state": "XTjj-nNrDm3qYRGyBux3Rezx7EHfy65zYwpwcs-Jl5Y",
            "nonce": "80LKWcdVwj5LtEg7RyfF-egGfh732LKwB4_lckEV5k8",
        }

        auth_response = requests.get(
            self.authorize_url, params=params, allow_redirects=False
        )

        if auth_response.status_code == 302:
            location = auth_response.headers.get("Location", "")
            code = location.split("code=")[1].split("&")[0]
            return self.exchange_code_for_tokens(code)

        raise Exception(
            f"Failed to get authorization code: {auth_response.status_code}"
        )

    def exchange_code_for_tokens(self, code):
        payload = {
            "code": code,
            "code_verifier": "3vnrGc340e_X7Ui44EoxuMsflq97PiVmgMaPidbdG8c",
            "redirect_uri": self.redirect_uri,
            "client_id": self.client_id,
            "grant_type": "authorization_code",
        }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "User-Agent": "Python-Script/1.0",
        }

        response = requests.post(self.token_url, data=payload, headers=headers)

        if response.status_code == 200:
            token_data = response.json()
            self.access_token = token_data.get("access_token")
            self.refresh_token = token_data.get("refresh_token")
            expires_in = token_data.get("expires_in", 3600)
            self.token_expiry = datetime.now() + timedelta(seconds=expires_in)
            return self.access_token

        raise Exception(f"Failed to get token: {response.status_code}")

    def refresh_access_token(self):
        payload = {
            "refresh_token": self.refresh_token,
            "client_id": self.client_id,
            "grant_type": "refresh_token",
        }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "User-Agent": "Python-Script/1.0",
        }

        response = requests.post(self.token_url, data=payload, headers=headers)

        if response.status_code == 200:
            token_data = response.json()
            self.access_token = token_data.get("access_token")
            self.refresh_token = token_data.get("refresh_token", self.refresh_token)
            expires_in = token_data.get("expires_in", 3600)
            self.token_expiry = datetime.now() + timedelta(seconds=expires_in)
            return self.access_token

        raise Exception(f"Failed to refresh token: {response.status_code}")

    def get_valid_token(self):
        if not self.access_token or not self.token_expiry:
            return self.authenticate()

        if datetime.now() >= self.token_expiry:
            return self.refresh_access_token()

        return self.access_token


# # Usage
# okta_auth = OktaAuth()

# # Use this in a loop or whenever you need a token
# try:
#     token = okta_auth.get_valid_token()
#     print(f"Valid token: {token}")
# except Exception as e:
#     print(f"Error: {str(e)}")
