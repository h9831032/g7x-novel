import sys
import json

def convert(input_path, output_path):
    missions = []
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    missions.append(json.loads(line))
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump({"missions": missions}, f, indent=4)
        print(f">>> [CONVERT SUCCESS] {input_path} -> {output_path}")
    except Exception as e:
        print(f">>> [CONVERT FAIL] {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python convert.py <input.jsonl> <output.json>")
        sys.exit(1)
    convert(sys.argv[1], sys.argv[2])