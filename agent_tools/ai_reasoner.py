from schema.models import *
from openai import OpenAI 
from agent_tools.utils import *
import json
import subprocess

class AIReasoner:
    def __init__(self, model: str = "llama3:8b"):
        self.model = model

    def explain_error(self, input_data: AIReasonerInput) -> str:
        prompt = self.build_prompt(input_data)
        return self.call_llm(prompt)
    
    def build_prompt(input_data: AIReasonerInput) -> str:
        error = input_data.error

        return f"""
            You are an incident analysis assistant.

            You are given FACTS produced by deterministic agent.
            You NUST NOT change or question the agent's classification.
            Your task is ONLY to explain the classification in clear human language.

            FACTS: 
            - Process name: {input_data.process_name}
            - Job ID: {input_data.job_id}
            - Error activity: {error.activity}
            - Error message: {error.timestamp}
            - Agent classification: {input_data.handling_status.value}

            RULES:
            - Do NOT invent causes
            - Do NOT suggest facts
            - Do NOT change the classification
            - If classification is UNHANDLED, explain why it likely caused job failure
            - If classification is AMBIGUOUS, explain what is missing
            - If classification is HANDLED, explain how recovery is implied
            Produce a short, clear explanation suitable for an operations engineer.
""".strip()
    
    def call_llm(self, prompt: str) -> str:
        process = subprocess.Popen(
            ["ollama", "run", self.model],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        stdout, stderr = process.communicate(prompt)

        if process.returncode != 0:
            raise RuntimeError(f"LLM error: {stderr}")
        return stdout.strip()
    
