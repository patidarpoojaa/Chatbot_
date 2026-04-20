import json
import ast

# Read current engine code
with open('backend/chatbot_engine.py', 'r', encoding='utf-8') as f:
    engine_code = f.read()

# Extract old map using ast
tree = ast.parse(engine_code)
old_map = {}
for node in ast.walk(tree):
    if isinstance(node, ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == 'EXACT_INTENT_MAP':
                # We found it! Let's evaluate it safely.
                # Actually, ast.literal_eval is better.
                try:
                    old_map = ast.literal_eval(node.value)
                except Exception:
                    pass

# Read new map
with open('new_exact_map.json', 'r', encoding='utf-8') as f:
    new_map = json.load(f)

# Merge
merged_map = old_map.copy()
merged_map.update(new_map)

# Now, we need to replace the section from EXACT_INTENT_MAP to expanded = self._expand(cleaned)
start_str = "        EXACT_INTENT_MAP = {"
end_str = "        expanded = self._expand(cleaned)"

start_idx = engine_code.find(start_str)
end_idx = engine_code.find(end_str)

if start_idx == -1 or end_idx == -1:
    print("Could not find the block to replace!")
    import sys
    sys.exit(1)

# Generate new code block
map_code_lines = ["        EXACT_INTENT_MAP = {"]
for k, v in merged_map.items():
    map_code_lines.append(f'            "{k}": "{v}",')
map_code_lines.append("        }")
map_code_lines.append("        if cleaned in EXACT_INTENT_MAP:")
map_code_lines.append("            target = EXACT_INTENT_MAP[cleaned]")
map_code_lines.append("            for i, intent in enumerate(self.intents):")
map_code_lines.append("                if intent == target:")
map_code_lines.append("                    return self.answers[i]")
map_code_lines.append("\n")

new_block = "\n".join(map_code_lines)

new_engine_code = engine_code[:start_idx] + new_block + engine_code[end_idx:]

with open('backend/chatbot_engine.py', 'w', encoding='utf-8') as f:
    f.write(new_engine_code)

print(f"Updated engine code successfully. Merged map size: {len(merged_map)}")
