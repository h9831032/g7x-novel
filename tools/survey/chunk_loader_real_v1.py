import os
class ChunkLoader:
    def __init__(self):
        self.stats = {"scanned": 0, "loaded": 0, "skipped": 0}
    def load(self, path):
        self.stats["scanned"] += 1
        if os.path.getsize(path) < 100:
            self.stats["skipped"] += 1
            return None
        self.stats["loaded"] += 1
        return open(path, 'r', encoding='utf-8', errors='ignore').read()
