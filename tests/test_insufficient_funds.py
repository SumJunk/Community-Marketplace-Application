import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

class TestInsufficientFundsModal(unittest.TestCase):
    def setUp(self):
        """Setup the Chrome WebDriver and navigate to the test page."""
        # Set up Chrome WebDriver
        self.service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=self.service)
        
        # The URL should point to the route where your insufficient_funds.html is served
        self.driver.get("http://localhost:5000/insufficient-funds")

    def test_insufficient_funds_modal(self):
        """Test the visibility and content of the insufficient funds modal."""
        # Example: Trigger the modal by simulating a condition where funds are insufficient
        # This could be clicking a button or automatically on page load.
        trigger_button = self.driver.find_element(By.ID, "triggerModalButton")
        trigger_button.click()

        # Check if the modal is displayed
        modal = self.driver.find_element(By.ID, "insufficientFundsModal")
        self.assertTrue(modal.is_displayed())

        # Check the content of the modal
        message = modal.find_element(By.TAG_NAME, "p").text
        self.assertIn("You do not have enough funds", message)

    def tearDown(self):
        """Tear down the test by closing the browser."""
        self.driver.quit()

if __name__ == "__main__":
    unittest.main()
