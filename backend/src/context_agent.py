import numpy as np

class ContextAgent:
    def __init__(self, window_size=5, decay=0.85, threshold=0.5):
        self.window_size = window_size
        self.decay = decay
        self.threshold = threshold
        self.history = []
        self.escalation_factor = 0

        # improved weights
        self.alpha = 0.45
        self.beta = 0.30
        self.gamma = 0.15
        self.delta = 0.20

    def update(self, threat_score):
        self.history.append(threat_score)
        if len(self.history) > self.window_size:
            self.history.pop(0)

        weights = np.array([self.decay ** i for i in range(len(self.history))])[::-1]
        memory_avg = np.sum(np.array(self.history) * weights) / np.sum(weights)

        freq = np.mean(np.array(self.history) > self.threshold)

        # improved escalation
        if threat_score > self.threshold + 0.25:
            self.escalation_factor += 0.08 * threat_score
        else:
            self.escalation_factor *= 0.9

        risk = (
            self.alpha * threat_score +
            self.beta * memory_avg +
            self.gamma * freq +
            self.delta * self.escalation_factor
        )

        # pattern amplification
        risk *= (1 + freq * 0.5)

        return min(risk, 1.0)
