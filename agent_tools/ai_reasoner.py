from schema.models import *
from agent_tools.utils import *
import json
import subprocess

class AIReasoner:
    def __init__(self, model: str = "llama3:8b"):
        self.model = model

    def explain_error(self, input_data: AIReasonerInput) -> str:
        prompt = self.build_prompt(input_data)
        return self.call_llm(prompt)
    
    def build_prompt(self, input_data: AIReasonerInput) -> str:
        error = input_data.error
        return f"""
You are an incident explanation assistant.

You MUST follow these rules:
- Use ONLY the facts provided below
- Do NOT guess causes
- Do NOT assume job failure unless explicitly stated
- Do NOT suggest fixes
- If information is missing, say "information is insufficient"

FACTS (do not go beyond these):
- Error message: {input_data.error.message}
- Activity: {input_data.error.activity}
- Timestamp: {input_data.error.timestamp}
- Agent classification: {input_data.handling_status.value}

TASK:
Explain in plain English:
1. What is known to have happened
2. Why the agent classified it as {input_data.handling_status.value}
3. What information is missing

Your explanation must stay factual and cautious.
""".strip()

    def call_llm(self, prompt: str) -> str:
        process = subprocess.Popen(
            ["ollama", "run", self.model],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8"
        )

        stdout, stderr = process.communicate(prompt)

        if process.returncode != 0:
            raise RuntimeError(f"LLM error: {stderr}")
        return stdout.strip()
    
