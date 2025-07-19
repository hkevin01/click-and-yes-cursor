# Click and Yes Cursor

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](https://github.com/hkevin01/click-and-yes-cursor/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## Project Overview
This project automates clicking specific coordinates (e.g., for a chat window) and pastes a configurable message (such as "yes, continue") at the target location. It is designed to streamline repetitive UI interactions, such as confirming prompts in chatbots or automated workflows.

**Features include:**
- Badges for build status, license, Python version, and code style
- Automated logging of all actions and test results in the `logs` folder
- Comprehensive test suite in the `tests` folder
- Modular, maintainable codebase with clear documentation

## Features
- Clicks at user-defined coordinates.
- Pastes a configurable message from `src/config.json`.
- Supports continuous improvement: regularly update `project_plan.md` and `test_plan.md`.
- Keeps a log of changes and test outputs in the `logs` folder for review and troubleshooting.
- Modular, maintainable codebase with clear documentation.

## Installation

### Node.js
```bash
npm install
```

### Python
```bash
pip install -r requirements.txt
```

## Usage

- Configure the coordinates and message in `src/config.json`.
- Run the automation script:
  - For Node.js: `npm start`
  - For Python: `python scripts/click_and_type.py`
- Logs for changes and test outputs are saved in the `logs` folder.

## Continuous Improvement Guidelines
- Update `.gitignore` whenever new files or directories are added.
- Regularly refactor code and expand test coverage.
- Document all changes in `project_plan.md` and `test_plan.md`.
- Incorporate new features and feedback iteratively.

## Troubleshooting
- Ensure dependencies are installed (`robotjs` for Node.js, `pyautogui`, `pyperclip`, `PyQt5` for Python).
- If automation fails, check error messages and logs for details.
- Update coordinates and message in `src/config.json` as needed.

## Community & Support
- For questions, feedback, or feature requests, open an issue or join discussions in the repository.
- See CONTRIBUTING.md for how to get involved.

## Contribution Guidelines
See `CONTRIBUTING.md` for details on how to contribute.

## License
MIT

## Running Without a Virtual Environment

You can run the automation without a Python virtual environment by installing the required dependencies system-wide (or for your user):

1. Install dependencies:
   ```bash
   pip3 install --user pyautogui pyperclip PyQt5
   # Or, to install all requirements:
   pip3 install --user -r requirements.txt
   ```

2. Run the automation script:
   ```bash
   ./run.sh
   # or
   bash run.sh
   ```

3. (Optional) To configure via GUI, run:
   ```bash
   ./gui_superuser.sh
   ```

**Note:**
- You do not need to activate a virtual environment.
- If you want to revert to using a virtual environment, recreate it with `python3 -m venv venv` and install requirements there.

## Cross-Platform Setup & Troubleshooting

### Linux
- Requires `scrot` and `python3-tk` for full pyautogui support:
  ```bash
  sudo apt-get install scrot python3-tk
  ```
- If clipboard or GUI features fail, check for missing dependencies above.

### Windows
- Ensure you install dependencies with:
  ```bash
  pip install --user pyautogui pyperclip
  ```
- No extra requirements, but you may need to run as administrator for some automation features.

### macOS
- Install dependencies with:
  ```bash
  pip3 install --user pyautogui pyperclip
  ```
- You may need to grant accessibility permissions to Terminal or Python in System Preferences > Security & Privacy > Accessibility.

If you see an error about missing dependencies, follow the printed instructions or see this section.

## Plugin/Extension Support

You can extend the automation by adding plugins to the `plugins/` directory. Each plugin should be a Python file with a `run()` function. Plugins can be used to perform custom actions before or after the main automation action.

### How to Add a Plugin
1. Create a Python file in the `plugins/` directory (e.g., `plugins/my_plugin.py`).
2. Define a `run()` function. It can accept optional arguments (e.g., the current message, coordinates, etc.).
3. The automation will call all plugins in the `plugins/` directory before each automation run.

**Example plugin:**
```python
# plugins/print_message.py
def run(message=None, coords=None):
    print(f"[PLUGIN] Message: {message}, Coords: {coords}")
```

### How Plugins Are Called
- All plugins in the `plugins/` directory are imported and their `run()` function is called before each automation run.
- Plugins can be used for logging, notifications, custom integrations, etc.

## Web/REST API for Control

You can control and monitor the automation via a simple REST API using FastAPI.

### Running the API Server
1. Install FastAPI and Uvicorn:
   ```bash
   pip3 install --user fastapi uvicorn
   ```
2. Start the server:
   ```bash
   uvicorn api_server:app --reload
   ```

### API Endpoints
- `GET /status` — Get current config and last 10 log lines
- `GET /config` — Get the current config
- `POST /config` — Update the config (send JSON body)
- `GET /log` — View the full run log

You can use `curl`, Postman, or your browser to interact with these endpoints.
