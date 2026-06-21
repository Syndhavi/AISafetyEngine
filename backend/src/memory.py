from collections import deque

class EpisodicMemory:
    def __init__(self, window_size=5):
        self.memory = deque(maxlen=window_size)

    def add(self, message):
        self.memory.append(message)

    def get_recent(self):
        return list(self.memory)
