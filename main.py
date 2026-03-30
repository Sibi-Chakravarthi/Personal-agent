from dotenv import load_dotenv
load_dotenv()

from core.agent import Agent

def main():
    agent = Agent()
    print("Agent ready. Type 'quit' to exit, 'clear' to reset conversation.\n")
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ("quit", "exit"):
            break
        if user_input.lower() == "clear":
            agent.clear_history()
            continue
        if not user_input:
            continue
        response = agent.run(user_input)
        print(f"\nAssistant: {response}\n")

if __name__ == "__main__":
    main()