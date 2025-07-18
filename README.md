# Click and Yes Cursor

## Project Overview
This project automates clicking specific coordinates (e.g., for a chat window) and types "yes, continue" before clicking or hitting enter. It is designed to streamline repetitive UI interactions, such as confirming prompts in chatbots or automated workflows.

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

- Configure the coordinates and window target in `src/config.json`.
- Run the automation script:
  - For Node.js: `npm start`
  - For Python: `python scripts/click_and_type.py`

## Troubleshooting
- Ensure dependencies are installed (`robotjs` for Node.js, `pyautogui` for Python).
- If automation fails, check error messages for details.
- Update coordinates in `src/config.json` as needed.

## Community & Support
- For questions, feedback, or feature requests, open an issue or join discussions in the repository.
- See CONTRIBUTING.md for how to get involved.

## Contribution Guidelines
See `CONTRIBUTING.md` for details on how to contribute.

## License
MIT
