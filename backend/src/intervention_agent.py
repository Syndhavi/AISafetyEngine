from llama_cpp import Llama

class InterventionAgent:

    def __init__(self, model_path=None):

        if model_path:
            print("Loading Phi-2...")
            self.llm = Llama(
                model_path=model_path,
                n_ctx=2048,
                n_threads=8
            )
            print("LLM Loaded.")
        else:
            self.llm = None
    def close(self):
        if self.llm is not None:
            try:
                self.llm = None
                print("✅ LLM cleaned up")
            except Exception as e:
                print("Cleanup error:", e)
    def threshold_decision(self, risk_score):

        if risk_score > 0.85:
            return "ALERT_GUARDIAN"
        elif risk_score > 0.7:
            return "BLOCK"
        elif risk_score > 0.4:
            return "WARN"
        else:
            return "ALLOW"

    def llm_decision(self, message, history):

        context_text = "\n".join(history)

        prompt = f"""You are a safety intrusion detection agent.

    Conversation history:
    {context_text}

    Latest message:
    {message}

    Classify the situation strictly as one of:
    ALLOW
    WARN
    BLOCK
    ALERT_GUARDIAN

    Answer:"""

        output = self.llm(
            prompt,
            max_tokens=5,
            temperature=0.0,  # deterministic
        )

        response = output["choices"][0]["text"].strip().upper()

        if "ALERT" in response:
            return "ALERT_GUARDIAN"
        elif "BLOCK" in response:
            return "BLOCK"
        elif "WARN" in response:
            return "WARN"
        else:
            return "ALLOW"

    def decide(self, message, threat_score, risk_score, history):

        if self.llm is None:
            return self.threshold_decision(risk_score)

        if risk_score < 0.7:
            return self.threshold_decision(risk_score)

        return self.llm_decision(message, history)
