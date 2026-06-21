from context_agent import ContextAgent

agent = ContextAgent()

messages_scores = [0.1, 0.7, 0.8, 0.4, 0.9]

for score in messages_scores:
    risk = agent.update(score)
    print(f"Threat: {score:.2f} → Risk: {risk:.2f}")