#!/usr/bin/env python3
import json
import os

# Read current config
config_path = os.path.join(os.path.dirname(__file__), '../src/config.json')
with open(config_path, 'r') as f:
    config = json.load(f)

# Fix message format - extract text from dictionary format
messages = config.get('message', [])
if messages and isinstance(messages[0], dict):
    # Convert dict format to simple strings
    config['message'] = [msg['text'] if isinstance(msg, dict) else msg for msg in messages]
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    print("Fixed message format in config.json")
else:
    print("Message format is already correct")
