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
