import unittest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import HtmlTestRunner  # For graphical reports

from app import app  # Import your Flask app

class TestWebApp(unittest.TestCase):

    def setUp(self):
        """Set up for each test method."""
        self.browser = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        self.live_server_url = "http://localhost:5000" # Default Flask development server URL

        # You might want to register a test user here if some tests depend on login
        self._register_test_user()

    def tearDown(self):
        """Clean up after each test method."""
        self.browser.quit()

    def _register_test_user(self):
        """Helper method to register a test user."""
        self.browser.get(self.live_server_url + '/register')
        self.browser.find_element(By.ID, "username").send_keys("Test User")
        self.browser.find_element(By.ID, "email").send_keys("test@example.com")
        self.browser.find_element(By.ID, "password").send_keys("password123")
        self.browser.find_element(By.ID, "confirm_password").send_keys("password123")
        self.browser.find_element(By.XPATH, "//button[text()='Register']").click()
        WebDriverWait(self.browser, 10).until(EC.url_contains('/details'))
        self.browser.find_element(By.ID, "dob").send_keys("2000-01-01")
        self.browser.find_element(By.ID, "avg_glucose_level").send_keys("90")
        self.browser.find_element(By.ID, "bmi").send_keys("22")
        self.browser.find_element(By.XPATH, "//button[text()='Submit Details']").click()
        WebDriverWait(self.browser, 10).until(EC.url_contains('/login'))

    def _login_test_user(self):
        """Helper method to log in the test user."""
        self.browser.get(self.live_server_url + '/login')
        self.browser.find_element(By.ID, "email").send_keys("test@example.com")
        self.browser.find_element(By.ID, "password").send_keys("password123")
        self.browser.find_element(By.XPATH, "//button[text()='Login']").click()
        WebDriverWait(self.browser, 10).until(EC.url_contains('/'))

    def test_home_page_loads(self):
        """Test if the home page loads correctly."""
        self.browser.get(self.live_server_url + '/')
        self.assertEqual(self.browser.title, "Stroke Sense") # Assuming your title is "Stroke Sense"

    def test_login_page_loads(self):
        """Test if the login page loads."""
        self.browser.get(self.live_server_url + '/login')
        self.assertIn("Login", self.browser.page_source)
        self.assertEqual(self.browser.title, "Login") # Adjust if your login page has a specific title

    def test_register_page_loads(self):
        """Test if the registration page loads."""
        self.browser.get(self.live_server_url + '/register')
        self.assertIn("Register", self.browser.page_source)
        self.assertEqual(self.browser.title, "Register") # Adjust if your register page has a specific title

    def test_successful_registration(self):
        """Test user registration flow."""
        self.browser.get(self.live_server_url + '/register')
        self.browser.find_element(By.ID, "username").send_keys("New Test User")
        self.browser.find_element(By.ID, "email").send_keys("newtest@example.com")
        self.browser.find_element(By.ID, "password").send_keys("password123")
        self.browser.find_element(By.ID, "confirm_password").send_keys("password123")
        self.browser.find_element(By.XPATH, "//button[text()='Register']").click() # Adjust XPath if needed

        WebDriverWait(self.browser, 10).until(EC.url_contains('/details'))
        self.assertIn("Personal Details", self.browser.page_source)
        self.assertEqual(self.browser.title, "Personal Details") # Adjust if your details page has a specific title

        # Fill in details page (basic data)
        self.browser.find_element(By.ID, "dob").send_keys("2001-02-03")
        self.browser.find_element(By.ID, "avg_glucose_level").send_keys("95")
        self.browser.find_element(By.ID, "bmi").send_keys("23")
        self.browser.find_element(By.XPATH, "//button[text()='Submit Details']").click() # Adjust XPath if needed

        WebDriverWait(self.browser, 10).until(EC.url_contains('/login'))
        self.assertIn("Account created successfully!", self.browser.page_source)

    def test_failed_login_incorrect_password(self):
        """Test login with incorrect password."""
        self.browser.get(self.live_server_url + '/login')
        self.browser.find_element(By.ID, "email").send_keys("test@example.com") # Assuming this user exists
        self.browser.find_element(By.ID, "password").send_keys("wrongpassword")
        self.browser.find_element(By.XPATH, "//button[text()='Login']").click() # Adjust XPath if needed
        self.assertIn("Invalid password", self.browser.page_source)

    def test_successful_login(self):
        """Test successful login with registered user."""
        self._login_test_user()
        self.assertEqual(self.browser.current_url, self.live_server_url + '/')
        self.assertIn("Stroke Sense", self.browser.page_source) # Check for a unique element on the home page after login

    def test_access_stroke_input_page(self):
        """Test if the stroke input page loads."""
        self.browser.get(self.live_server_url + '/stroke-input')
        self.assertIn("Stroke Prediction Input", self.browser.page_source) # Adjust based on your page content
        self.assertEqual(self.browser.title, "Stroke Prediction") # Adjust if your prediction page has a specific title

    def test_predict_no_stroke(self):
        """Test stroke prediction with low-risk factors."""
        self.browser.get(self.live_server_url + '/stroke-input')
        self.browser.find_element(By.NAME, "gender").send_keys("0") # Female
        self.browser.find_element(By.NAME, "age").send_keys("35")
        self.browser.find_element(By.NAME, "hypertension").send_keys("0")
        self.browser.find_element(By.NAME, "heart_disease").send_keys("0")
        self.browser.find_element(By.NAME, "avg_glucose_level").send_keys("85")
        self.browser.find_element(By.NAME, "bmi").send_keys("21")
        self.browser.find_element(By.XPATH, "//button[text()='Predict']").click() # Adjust XPath if needed
        WebDriverWait(self.browser, 10).until(EC.url_contains('/predict'))
        self.assertIn("The person is unlikely to have a stroke.", self.browser.page_source)
        self.assertEqual(self.browser.title, "Stroke Prediction Result") # Adjust if your result page has a specific title

    def test_predict_potential_stroke(self):
        """Test stroke prediction with high-risk factors."""
        self.browser.get(self.live_server_url + '/stroke-input')
        self.browser.find_element(By.NAME, "gender").send_keys("1") # Male
        self.browser.find_element(By.NAME, "age").send_keys("65")
        self.browser.find_element(By.NAME, "hypertension").send_keys("1")
        self.browser.find_element(By.NAME, "heart_disease").send_keys("1")
        self.browser.find_element(By.NAME, "avg_glucose_level").send_keys("190")
        self.browser.find_element(By.NAME, "bmi").send_keys("32")
        self.browser.find_element(By.XPATH, "//button[text()='Predict']").click() # Adjust XPath if needed
        WebDriverWait(self.browser, 10).until(EC.url_contains('/predict'))
        self.assertIn("The person is likely to have a stroke.", self.browser.page_source)
        self.assertEqual(self.browser.title, "Stroke Prediction Result") # Adjust if your result page has a specific title

    def test_access_user_profile_logged_out(self):
        """Test accessing user profile when logged out."""
        self.browser.get(self.live_server_url + '/userprofile')
        self.assertIn("Please log in to view your profile.", self.browser.page_source)
        self.assertEqual(self.browser.current_url, self.live_server_url + '/login')
        self.assertEqual(self.browser.title, "Login") # Assuming redirection goes to login page

    def test_access_user_profile_logged_in(self):
        """Test accessing user profile when logged in."""
        self._login_test_user()
        self.browser.get(self.live_server_url + '/userprofile')
        self.assertIn("User Profile", self.browser.page_source) # Adjust based on your profile page content
        self.assertEqual(self.browser.title, "User Profile") # Adjust if your profile page has a specific title

    def test_access_edit_profile_logged_out(self):
        """Test accessing edit profile when logged out."""
        self.browser.get(self.live_server_url + '/edit-profile')
        # You might have a specific message or redirection when trying to access when logged out
        self.assertIn("Please log in", self.browser.page_source) # Adjust based on your implementation
        self.assertTrue(self.browser.current_url.startswith(self.live_server_url + '/login')) # Or a similar check

    def test_access_edit_profile_logged_in(self):
        """Test accessing edit profile when logged in."""
        self._login_test_user()
        self.browser.get(self.live_server_url + '/edit-profile')
        self.assertIn("Edit Profile", self.browser.page_source) # Adjust based on your edit profile content
        self.assertEqual(self.browser.title, "Edit Profile") # Adjust if your edit profile page has a specific title

    def test_access_admin_panel(self):
        """Test if the admin panel page loads (no login check here)."""
        self.browser.get(self.live_server_url + '/admin')
        self.assertIn("Admin Panel", self.browser.page_source) # Adjust based on your admin panel content
        self.assertEqual(self.browser.title, "Admin Panel") # Adjust if your admin panel page has a specific title

    def test_access_feedback_page(self):
        """Test if the feedback page loads."""
        self.browser.get(self.live_server_url + '/feedback')
        self.assertIn("Feedback", self.browser.page_source) # Adjust based on your page content
        self.assertEqual(self.browser.title, "Feedback") # Adjust if your feedback page has a specific title

    def test_access_services_page(self):
        """Test if the services page loads."""
        self.browser.get(self.live_server_url + '/services')
        self.assertIn("Services", self.browser.page_source) # Adjust based on your page content
        self.assertEqual(self.browser.title, "Services") # Adjust if your services page has a specific title

    def test_access_koa_page(self):
        """Test if the 'koa' (Coming Soon) page loads."""
        self.browser.get(self.live_server_url + '/koa')
        self.assertIn("Coming Soon", self.browser.page_source) # Adjust based on your page content
        self.assertEqual(self.browser.title, "Coming Soon") # Adjust if your coming soon page has a specific title

    def test_access_skin_cancer_page(self):
        """Test if the 'skin-cancer' (Coming Soon) page loads."""
        self.browser.get(self.live_server_url + '/skin-cancer')
        self.assertIn("Coming Soon", self.browser.page_source) # Adjust based on your page content
        self.assertEqual(self.browser.title, "Coming Soon") # Adjust if your coming soon page has a specific title

    def test_logout_functionality(self):
        """Test user logout functionality."""
        self._login_test_user()
        try:
            logout_link = self.browser.find_element(By.LINK_TEXT, "Logout") # Adjust the link text if needed
            logout_link.click()
            WebDriverWait(self.browser, 10).until(EC.url_contains('/')) # Assuming logout redirects to home
            self.assertIn("You have been logged out.", self.browser.page_source)
            self.assertEqual(self.browser.title, "Stroke Sense") # Or your home page title
        except NoSuchElementException:
            self.fail("Logout link not found on the page.")

    def test_access_tp_page(self):
        """Test if the 'tp' page loads."""
        self.browser.get(self.live_server_url + '/tp')
        self.assertIn("tp", self.browser.page_source) # Adjust based on your page content
        self.assertEqual(self.browser.title, "tp") # Adjust if your tp page has a specific title

    def test_access_nonexistent_page(self):
        """Test accessing a non-existent page (404 error)."""
        self.browser.get(self.live_server_url + '/thispagedoesnotexist')
        self.assertIn("Not Found", self.browser.page_source) # Adjust based on your 404 page content
        self.assertEqual(self.browser.title, "404 Not Found") # Adjust if your 404 page has a specific title
        self.assertEqual(self.browser.status_code, 404) # Verify the HTTP status code

if __name__ == '__main__':
    # Create a test suite
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestWebApp))

    # Open a file to write the HTML report
# Open a file to write the HTML report
    with open("test_report.html", "w") as f:
        runner = HtmlTestRunner.HTMLTestRunner(
            stream=f,
            # title='Stroke Sense Website Test Report',  # Remove this line
            # description='Results of functional tests'   # Remove this line
        )
        runner.run(suite)