from collections import Counter, deque


class TemporalFilter:
    def __init__(self, buffer_size=7, stable_min_count=4, empty_label="none"):
        self.buffer = deque(maxlen=buffer_size)
        self.stable_min_count = stable_min_count
        self.empty_label = empty_label
        self.current_stable_label = empty_label

    def append(self, label):
        self.buffer.append(label)
        return self.get_stable_label()

    def get_stable_label(self):
        if not self.buffer:
            self.current_stable_label = self.empty_label
            return self.current_stable_label

        top_label, top_count = Counter(self.buffer).most_common(1)[0]
        if top_count >= self.stable_min_count:
            self.current_stable_label = top_label
        else:
            self.current_stable_label = self.empty_label
        return self.current_stable_label

    def clear(self):
        self.buffer.clear()
        self.current_stable_label = self.empty_label
