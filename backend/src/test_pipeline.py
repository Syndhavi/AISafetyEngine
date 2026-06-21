from inference_engine import process_message
from context_agent import ContextAgent
from intervention_agent import InterventionAgent
from memory import EpisodicMemory

memory = EpisodicMemory(window_size=5)

intervention = InterventionAgent(
    model_path="models/phi-2.Q4_K_M.gguf"
)

agent = ContextAgent()

test_messages = [
    "Hello how are you",
    "Send your pic?",
    "Are you a virgin?",
    "Fuck bro",
    "You are a stupid",
    "Can you send your nude picture?",
    "Have a nice day"
]

for msg in test_messages:
    memory.add(msg)
    history = memory.get_recent()
    threat = process_message(msg)
    risk = agent.update(threat)
    action = intervention.decide(
    msg,
    threat,
    risk,
    history
)
    

    print(f"Message: {msg}")
    print(f"Threat Score: {threat:.4f}")
    print(f"Context Risk: {risk:.4f}")
    print(f"Action: {action}")
    print("-" * 40)
    intervention.llm = None
