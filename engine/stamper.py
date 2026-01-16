import json, os
class Stamper:
    def __init__(self, d): self.p = os.path.join(d, "stamp_manifest.json")
    def stamp(self, items): 
        with open(self.p, "w", encoding="utf-8") as f: json.dump(items, f, indent=4)