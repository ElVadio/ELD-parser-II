# setup_production.py
import os
import subprocess
import argparse

def setup_production(env):
    """Setup production environment."""
    # Create necessary directories
    os.makedirs('logs', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    os.makedirs('models', exist_ok=True)

    # Setup environment variables
    env_vars = {
        'PROD': {
            'FLASK_ENV': 'production',
            'MODEL_PATH': '/app/models',
            'LOG_LEVEL': 'INFO'
        },
        'STAGING': {
            'FLASK_ENV': 'staging',
            'MODEL_PATH': '/app/models',
            'LOG_LEVEL': 'DEBUG'
        }
    }

    # Write environment variables
    with open('.env', 'w') as f:
        for key, value in env_vars[env].items():
            f.write(f'{key}={value}\n')

    # Setup logging
    subprocess.run(['python', 'setup_logging.py'])

    # Initialize database
    subprocess.run(['python', 'init_db.py'])

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--env', choices=['PROD', 'STAGING'], default='PROD')
    args = parser.parse_args()
    setup_production(args.env)