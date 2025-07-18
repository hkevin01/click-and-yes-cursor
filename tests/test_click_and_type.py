import logging
import os
import unittest
from logging.handlers import RotatingFileHandler

from scripts.click_and_type import click_and_paste, get_config

log_path = os.path.join(
    os.path.dirname(__file__), '../logs/test_click_and_type.log'
)
handler = RotatingFileHandler(log_path, maxBytes=1000000, backupCount=3)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[handler]
)


class TestClickAndType(unittest.TestCase):

    def test_click_and_type_callable(self):
        """Test if click_and_type is callable."""
        self.assertTrue(callable(click_and_paste))

    def test_get_coordinates(self):
        """Test if get_config returns valid x and y coordinates."""
        coords, _ = get_config()
        self.assertIn('x', coords)
        self.assertIn('y', coords)

    def test_workflow(self):
        try:
            coords, message = get_config()
            click_and_paste(coords['x'], coords['y'], message)
        except Exception as err:
            self.fail(
                f'click_and_paste threw an error: {err}'
            )


if __name__ == "__main__":
    unittest.main()
