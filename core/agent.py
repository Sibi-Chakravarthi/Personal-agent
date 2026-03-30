import json
import re
from core.llm import LLM
from tools import TOOLS, execute_tool

SYSTEM_PROMPT = """You are a personal AI assistant. You help with tasks by reasoning step by step and using tools when needed.

You have access to these tools:
{tool_descriptions}

To use a tool, respond in this exact format:
THOUGHT: your reasoning about what to do
ACTION: tool_name
ACTION_INPUT: {{"key": "value"}}

When you have a final answer, respond in this format:
THOUGHT: I now have enough information
FINAL_ANSWER: your response to the user

Rules:
- Always think before acting
- Only use one tool at a time
- Be concise in your final answer
- If a tool fails, try a different approach
- ONLY state facts that came from a tool result. Never use your training data for factual claims.
- If the user asks a follow-up, use context from previous messages in this conversation.
- If you need fresher data for a follow-up, search again with a more specific query.
"""

class Agent:
    def __init__(self):
        self.llm = LLM()
        self.max_steps = 6
        self.conversation_history = []

    def _build_tool_descriptions(self) -> str:
        return "\n".join(
            f"- {name}: {meta['description']}"
            for name, meta in TOOLS.items()
        )

    def _parse_response(self, text: str) -> dict:
        if "FINAL_ANSWER:" in text:
            answer = text.split("FINAL_ANSWER:")[-1].strip()
            return {"type": "final", "content": answer}

        action_match = re.search(r"ACTION:\s*(\w+)", text)
        input_match = re.search(r"ACTION_INPUT:\s*(\{.*?\})", text, re.DOTALL)
        thought_match = re.search(r"THOUGHT:\s*(.+?)(?=ACTION:|FINAL_ANSWER:|$)", text, re.DOTALL)

        if action_match and input_match:
            try:
                action_input = json.loads(input_match.group(1))
            except json.JSONDecodeError:
                action_input = {}
            return {
                "type": "action",
                "thought": thought_match.group(1).strip() if thought_match else "",
                "action": action_match.group(1).strip(),
                "input": action_input
            }

        return {"type": "unknown", "content": text}

    def run(self, user_input: str) -> str:
        self.conversation_history.append({"role": "user", "content": user_input})

        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT.format(
                    tool_descriptions=self._build_tool_descriptions()
                )
            },
            *self.conversation_history
        ]

        tool_calls_this_turn = []  # track what happened this turn

        for step in range(self.max_steps):
            try:
                response = self.llm.chat(messages)
            except Exception as e:
                return f"LLM error: {str(e)}"

            parsed = self._parse_response(response)

            if parsed["type"] == "final":
                # Build a rich history entry that includes tool context
                history_content = parsed["content"]
                if tool_calls_this_turn:
                    summary = " | ".join(
                        f"[searched: '{t['query']}' → {t['result'][:150]}]"
                        for t in tool_calls_this_turn
                    )
                    history_content = f"{parsed['content']}\n\n[Tools used: {summary}]"

                self.conversation_history.append({
                    "role": "assistant",
                    "content": history_content
                })
                return parsed["content"]

            elif parsed["type"] == "action":
                print(f"[Step {step+1}] {parsed['thought']}")
                print(f"  → Using tool: {parsed['action']} with {parsed['input']}")

                result = execute_tool(parsed["action"], parsed["input"])
                result_trimmed = result[:500]
                print(f"  ← Result: {result_trimmed[:100]}...")

                # Track tool calls for history
                tool_calls_this_turn.append({
                    "query": parsed["input"].get("query", str(parsed["input"])),
                    "result": result_trimmed
                })

                messages.append({"role": "assistant", "content": response})
                messages.append({
                    "role": "user",
                    "content": f"OBSERVATION: {result_trimmed}"
                })

            else:
                messages.append({"role": "assistant", "content": response})
                messages.append({
                    "role": "user",
                    "content": "Please continue. Use the ACTION format or give a FINAL_ANSWER."
                })

        return "I wasn't able to complete that task. Please try again."

    def clear_history(self):
        self.conversation_history = []
        print("Conversation history cleared.")