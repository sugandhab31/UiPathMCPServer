import requests, os, time, threading

class TokenManager:
    def __init__(self):        
        self._access_token = None
        self._expires_at = 0
        self._lock = threading.Lock()

    def get_access_token(self):
        try:
            now = time.time()
            with self._lock:
                if self._access_token and time.time() < self._expires_at - 60:
                    return self._access_token

            BASE_URL = "https://cloud.uipath.com/identity_/connect/token"
            client_id = os.getenv("UIPATH_CLIENT_ID")
            client_secret = os.getenv("UIPATH_CLIENT_SECRET")

            if not client_id or not client_secret:
                raise RuntimeError(
                    "Missing UiPath credentials. "
                    "Set UIPATH_CLIENT_ID and UIPATH_CLIENT_SECRET as environment variables."
                )
            payload = {
                "grant_type": "client_credentials",
                "client_id": client_id,
                "client_secret": client_secret,
                "scope": "OR.Default OR.Monitoring.Read OR.Robots.Read OR.Jobs.Read OR.Folders"
            }
            headers = {
                "Content-Type": "application/x-www-form-urlencoded"
            }

            for attempt in range(3):
                response = requests.post(
                    BASE_URL, 
                    data = payload, 
                    headers=headers, 
                    timeout=10
                )
                if response.ok:
                    data = response.json()
                    self._access_token = data["access_token"]
                    self._expires_at = now + data["expires_in"]
                    return self._access_token
                time.sleep(2**attempt)

            response.raise_for_status()
            
        except Exception as e:
            raise e