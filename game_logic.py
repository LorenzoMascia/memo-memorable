import random

class MemoryGameLogic:
    def __init__(self, size):
        self.size = size
        self.num_blocks = size * size
        self.pairs = self.num_blocks // 2
        self.blocks = self._generate_blocks()

    def _generate_blocks(self):
        values = list(range(1, self.pairs + 1)) * 2
        random.shuffle(values)
        return {f"block_{i}": val for i, val in enumerate(values)}

    def check_match(self, key1, key2):
        return self.blocks[key1] == self.blocks[key2]

    def remove_blocks(self, key1, key2):
        del self.blocks[key1]
        del self.blocks[key2]

    def get_value(self, key):
        return self.blocks.get(key)

    def has_won(self):
        return len(self.blocks) == 0
