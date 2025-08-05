# -----------------------------------------------------------------------------
# File Name   : PteroConnect.py
# Description : Provides the PteroConnect class to interact with the Pterodactyl
#               Panel API. Automatically detects whether the API key is an
#               admin or client token and handles connection headers.
#
# Author      : X
# Created On  : 05/08/2025
# Last Updated: 05/08/2025
# -----------------------------------------------------------------------------

import requests
import time
from .ConsoleMessage import ConsoleMessage

# Internal logger
log = ConsoleMessage()

class PteroConnect:
    def __init__(self, panel_url: str, api_key: str, debug: bool = False):
        self.panel_url = panel_url.rstrip("/")
        self.api_key = api_key
        self.api_type = None  # 'admin', 'client', or None
        self.debug = debug
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        self._detect_api_type()

    def _detect_api_type(self):

        # Try Admin API
        try:
            start = time.time()
            admin_resp = requests.get(
                f"{self.panel_url}/api/application/users",
                headers=self.headers,
                timeout=5
            )
            duration = time.time() - start
            if self.debug:
                log.debug(f"Admin API check took {duration:.2f} seconds")

            if admin_resp.status_code == 200:
                self.api_type = "admin"
                log.info("Logging in using static token")
                log.info("Admin API key detected.")
                return True
        except requests.RequestException as e:
            log.warning(f"Admin API check failed: {e}")
            return False

        # Try Client API
        try:
            start = time.time()
            client_resp = requests.get(
                f"{self.panel_url}/api/client",
                headers=self.headers,
                timeout=5
            )
            duration = time.time() - start
            if self.debug:
                log.debug(f"Client API check took {duration:.2f} seconds")

            if client_resp.status_code == 200:
                self.api_type = "client"
                log.info("Logging in using static token")
                log.info("Client API key detected.")
                return True

        except requests.RequestException as e:
            log.warning(f"Client API check failed: {e}")
            return False

        # Neither worked
        log.error("Invalid API key or insufficient permissions.")
        self.api_type = None

# -----------------------------------------------------------------------------
# End of File: PteroConnect.py
# -----------------------------------------------------------------------------