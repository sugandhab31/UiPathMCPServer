import requests, time

class ToolService:
    def __init__(self, token_provider,folder_id):
        self.token_provider = token_provider
        self.folderID = folder_id            #"5165358"
        self.Base_URL = "https://cloud.uipath.com/suganfluwktp/Sugandha/orchestrator_"
        self._session = requests.Session()

    def get_job_details(self, job_id: str, top: int = 2):
        access_token = self.token_provider.get_access_token()
        url = f"{self.Base_URL}/odata/Jobs({job_id})"        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
            "X-UIPATH-OrganizationUnitId": self.folderID
        }
        # params = {
        #     "$filter": f"JobId eq {job_id}",
        #     "$top": top,
        #     "$orderby": "TimeStamp desc"
        # }
        response =  requests.get(url=url, headers=headers)
        response.raise_for_status()
        return response.json()

    def get_Jobs(self, process_name:str, state: str):
        access_token = self.token_provider.get_access_token() 
        url = f"{self.Base_URL}/odata/Jobs"

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
            "X-UIPATH-OrganizationUnitId": self.folderID
        }

        params = {
            "$filter": f"ReleaseName eq '{process_name}' and State eq '{state}'",
            "$orderby": "EndTime desc",
            "$top": 1,
            "$skip": 0
        }

        for attempt in range(3):
            response = self._session.get(
                url, 
                headers=headers, 
                params=params,
                timeout=15
            )
            if response.ok:
                data = response.json().get("value",[])
                if not data:
                    return "No Jobs found."
                return data[0]
            time.sleep(2**attempt)

        response.raise_for_status()

        
    def get_Job_Logs(self, job_id:str):
        access_token = self.token_provider.get_access_token()
        url = f"{self.Base_URL}/odata/RobotLogs"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
            "X-UIPATH-OrganizationUnitId": self.folderID
        }

        all_logs = []
        skip = 0
        top = 100
        while True:
            params = {
                "$filter": f"JobKey eq {job_id}",
                "$skip": skip,
                "$top": top,
                "$order by": "Timestamp desc"
            }       
            response = self._session.get(
                url, 
                headers=headers, 
                params=params,
                timeout=15
            )
            response.raise_for_status()
            logs = response.json().get("value", [])
            all_logs.extend(logs)

            if len(logs)<top:
                break
            skip += top
        
        return all_logs
    


