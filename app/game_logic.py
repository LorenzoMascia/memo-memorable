import random

class MemoryGameLogic:
    def __init__(self, pairs):
        self.pairs = dict(pairs)
        self.inverse_pairs = {v: k for k, v in pairs}
        all_values = list(self.pairs.keys()) + list(self.pairs.values())
        random.shuffle(all_values)
        self.blocks = {f"block_{i}": val for i, val in enumerate(all_values)}

    def check_match(self, val1, val2):
        return self.pairs.get(val1) == val2 or self.inverse_pairs.get(val1) == val2

    def remove_blocks(self, key1, key2):
        if key1 in self.blocks:
            del self.blocks[key1]
        if key2 in self.blocks:
            del self.blocks[key2]

    def get_value(self, key):
        return self.blocks.get(key)

    def has_won(self):
        return len(self.blocks) == 0

