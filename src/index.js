// Click and Yes Cursor Automation
// Automates clicking coordinates and typing 'yes, continue' in a chat window

const robot = require('robotjs');
const fs = require('fs');

/**
 * Reads coordinates from config file or uses defaults
 */
function getCoordinates() {
    try {
        const config = JSON.parse(fs.readFileSync('./src/config.json', 'utf8'));
        return config.coordinates || { x: 100, y: 200 };
    } catch (e) {
        // Default coordinates if config not found
        return { x: 100, y: 200 };
    }
}

/**
 * Clicks at the given coordinates and types a message
 * @param {number} x - X coordinate
 * @param {number} y - Y coordinate
 * @param {string} message - Message to type
 */
function clickAndType(x, y, message = 'yes, continue') {
    try {
        robot.moveMouse(x, y);
        robot.mouseClick();
        robot.typeString(message);
        robot.keyTap('enter');
    } catch (err) {
        console.error('Automation error:', err);
    }
}

// Main execution
const coords = getCoordinates();
clickAndType(coords.x, coords.y);

module.exports = { clickAndType, getCoordinates };
