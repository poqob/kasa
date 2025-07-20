import os

def read_env_file(filepath='.env')->dict:
    env_vars = {}
    if not os.path.exists(filepath):
        return env_vars
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip().strip('"').strip("'")
    return env_vars
