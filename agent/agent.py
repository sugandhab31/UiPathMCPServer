import requests, os, datetime, time

class TokenManager:
    def __init__(self):        
        self._access_token = None
        self._expires_at = 0

    def get_access_token(self):
        try:
            now = time.time()
            if self._access_token is not None and now < self._expires_at - 120:
                print("fetching existing token")
                return self._access_token

            BASE_URL = "https://cloud.uipath.com/identity_/connect/token"
            client_id = os.getenv("UIPATH_CLIENT_ID")
            client_secret = os.getenv("UIPATH_CLIENT_SECRET")

            if not client_id or not client_secret:
                raise RuntimeError(
                    "Missing UiPath credentials. "
                    "Set UIPATH_CLIENT_ID and UIPATH_CLIENT_SECRET as environment variables."
                )
            print("new token")
            payload = {
                "grant_type": "client_credentials",
                "client_id": client_id,
                "client_secret": client_secret,
                "scope": "OR.Jobs.Read OR.Robots",
            }
            headers = {
                "Content-Type": "application/x-www-form-urlencoded"
            }
        
            response = requests.post(BASE_URL, data = payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            self._access_token = data["access_token"]
            self._expires_at = now + data["expires_in"]
            return self._access_token
        except Exception as e:
            raise e

def get_job_details(access_token:str, job_id: int, top: int = 5):
    url = "cloud.uipath.com/suganfluwktp/Sugandha/orchestrator_/odata/RobotLogs"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }
    params = {
        "$filter": f"JobId eq {job_id}",
        "$top": top,
        "$orderby": "TimeStamp desc"
    }
    response =  requests.get(url=url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()["value"]

tokenManager = TokenManager()
token = tokenManager.get_access_token()
print(token)

