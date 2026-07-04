import os
import json
import logging

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
log_dir = os.path.join(base_dir, 'log')

def get_state_file_path():
    return os.path.join(log_dir, 'resume_state.json')

def load_state():
    state_file = get_state_file_path()
    if os.path.exists(state_file):
        try:
            with open(state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_state(index, total_count):
    state_file = get_state_file_path()
    state = {'last_index': index, 'total_count': total_count}
    try:
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f)
    except Exception:
        pass

def clear_state():
    state_file = get_state_file_path()
    if os.path.exists(state_file):
        try:
            os.remove(state_file)
        except Exception:
            pass

