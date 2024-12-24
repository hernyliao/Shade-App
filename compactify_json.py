import json
import os

def compact_json(input_file, output_file):
    with open(input_file, 'r') as f:
        data = json.load(f)

    with open(output_file, 'w') as f:
        json.dump(data, f, separators=(',', ':'))

if __name__ == "__main__":
    base_path = os.path.dirname(__file__)
    input_file = os.path.join(base_path, 'data', 'Full_Building_List.json')
    output_file = os.path.join(base_path, 'data', 'Full_Building_List_Compact.json')
    
    compact_json(input_file, output_file)
    print(f"Compact JSON saved to {output_file}")