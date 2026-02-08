from agent_tools.utils import *
from agent_tools.ai_reasoner import *
from mcp.mcp_tools import TokenManager, ToolService
from schema import models
import json

def main():
    # Get new Token
    token_obj = TokenManager()
    print(token_obj.get_access_token())
    # # pass token to ToolService to get job Key
    # tool_obj = ToolService(token_provider=token_obj)
    # job_details = tool_obj.get_Jobs("DummyProcess","Faulted")
    # job_key = job_details["Key"]
    # # pass job key to fetch raw logs
    # raw_logs = tool_obj.get_Job_Logs(job_id=job_key)
    # # normalize the raw logs and sort according to timestamp
    # events = normalize_logs(raw_logs=raw_logs)
    # # print(data)
    # errors = extract_error_events(events)
    # handling = classify_error_handling(errors, events)
    # # for error_id, status in handling.items():
    # #     print(error_id, status.value)

    # AIReasonerInput.process_name = "DummyProcess"
    # AIReasonerInput.job_id = job_key
    # reasoner = AIReasoner()
    # for error in errors:
    #     AIReasonerInput.error = error
    #     AIReasonerInput.handling_status = error.handling_status
    #     print(f"\nError ID: {error.error_id}")
    #     print(f"Status: {error.handling_status.value}")
    #     explanation = reasoner.explain_error(AIReasonerInput)
    #     print("\nAI Explanation:")
    #     print(explanation)

    #starting optimizations

if __name__ == "__main__":
    main()
