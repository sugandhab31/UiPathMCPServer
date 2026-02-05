from agent_tools.utils import normalize_logs
from mcp.mcp_tools import TokenManager, ToolService
from schema import models
import json

def main():
    # Get new Token
    token_obj = TokenManager()
    # pass token to ToolService to get job Key
    tool_obj = ToolService(token_provider=token_obj)
    job_details = tool_obj.get_Jobs("DummyProcess","Faulted")
    job_key = job_details["Key"]
    raw_logs = tool_obj.get_Job_Logs(job_id=job_key)
    data = normalize_logs(raw_logs=raw_logs)
    print(data)

if __name__ == "__main__":
    main()
