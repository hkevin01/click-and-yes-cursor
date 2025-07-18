# Click and Yes Cursor

## Project Overview
This project automates clicking specific coordinates (e.g., for a chat window) and pastes a configurable message (such as "yes, continue") at the target location. It is designed to streamline repetitive UI interactions, such as confirming prompts in chatbots or automated workflows.

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
