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
                "scope": "OR.Default OR.Monitoring OR.Jobs OR.Robots OR.Folders"
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

class ToolService:
    def __init__(self, token_provider):
        self.token_provider = token_provider
        self.url = "https://cloud.uipath.com/suganfluwktp/Sugandha/orchestrator_"
        self.folderID = "5165358"

    def get_job_details(self, job_id: str, top: int = 2):
        access_token = self.token_provider.get_access_token()
        url = f"{self.url}/odata/Jobs({job_id})"        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
            "X-UIPATH-OrganizationUnitId": self.folderID
        }
        params = {
            "$filter": f"JobId eq {job_id}",
            "$top": top,
            "$orderby": "TimeStamp desc"
        }
        response =  requests.get(url=url, headers=headers)
        response.raise_for_status()
        return response.json()

    def get_Jobs(self, process_name:str, state: str):
        access_token = self.token_provider.get_access_token() 
        url = f"{self.url}/odata/Jobs"

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
            "X-UIPATH-OrganizationUnitId": self.folderID
        }

        params = {
            "$filter": f"ReleaseName eq '{process_name}' and State eq '{state}'",
            "$orderby": "EndTime desc",
            "$top": 1
        }

        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()

        jobs = response.json()

        if not jobs:
            return "No jobs found."
        print(response.status_code)
        return jobs["value"][0]["Id"]

    def get_Job_Logs(self, top:int, job_id:str):
        access_token = self.token_provider.get_access_token()
        url = f"{self.url}/odata/RobotLogs"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
            "X-UIPATH-OrganizationUnitId": self.folderID
        }

        params = {
        "$filter": f"JobId eq {job_id}",
        "$orderby": "TimeStamp desc",
        "$top": top
        }

        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()

        return response.json().get("value", [])




token = TokenManager()
obj = ToolService(token_provider=token)
jobid = obj.get_Jobs("DummyProcess","Faulted")
print(jobid)
job_details = obj.get_job_details(job_id=jobid)
# print(job_details)
logs = obj.get_Job_Logs(job_id=jobid, top=1)
print(logs)
