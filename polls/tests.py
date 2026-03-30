from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import Select

class MySeleniumTests(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        opts = Options()
        opts.add_argument("--headless")
        cls.selenium = WebDriver(options=opts)
        cls.selenium.implicitly_wait(5)

        # Creem superusuari inicial
        user = User.objects.create_user("isard", "isard@isardvdi.com", "pirineus")
        user.is_superuser = True
        user.is_staff = True
        user.save()

    @classmethod
    def tearDownClass(cls):
        # Tanquem el navegador un cop acabin els tests
        cls.selenium.quit()
        super().tearDownClass()

    def test_staff_permissions(self):
        # Fer login al web amb isard
        self.selenium.get('%s%s' % (self.live_server_url, '/admin/login/'))

        username_input = self.selenium.find_element(By.NAME, "username")
        username_input.send_keys('isard')

        password_input = self.selenium.find_element(By.NAME, "password")
        password_input.send_keys('pirineus')

        self.selenium.find_element(By.XPATH, '//input[@value="Log in"]').click()

        # Crear usuari staff
        self.selenium.get('%s%s' % (self.live_server_url, '/admin/'))
        self.selenium.find_element(By.XPATH, '//a[@href="/admin/auth/user/add/"]').click()

        username_input = self.selenium.find_element(By.ID, "id_username")
        username_input.send_keys('staff')

        password_input = self.selenium.find_element(By.ID, "id_password1")
        password_input.send_keys('IOCEAC2m3')

        password_confirmation_input = self.selenium.find_element(By.ID, "id_password2")
        password_confirmation_input.send_keys('IOCEAC2m3')

        self.selenium.find_element(By.XPATH, '//input[@value="Save and continue editing"]').click()

        # Assignar permisos de Staff i view Questions
        self.selenium.find_element(By.ID, "id_is_staff").click()
        select_permisos = Select(self.selenium.find_element(By.ID, "id_user_permissions_from"))
        select_permisos.select_by_visible_text("Polls | question | Can view question")
        self.selenium.find_element(By.ID, "id_user_permissions_add").click()
        self.selenium.find_element(By.XPATH, '//input[@value="Save"]').click()

        self.selenium.find_element(By.XPATH, '//a[@href="/admin/polls/question/add/"]').click()
        self.selenium.find_element(By.ID, "id_question_text").send_keys("Pregunta de prova EAC2")
        self.selenium.find_element(By.ID, "id_pub_date_0").send_keys("2026-03-30")
        self.selenium.find_element(By.ID, "id_pub_date_1").send_keys("12:00:00")
        self.selenium.find_element(By.NAME, "_save").click()

        # Fer logout d'isard i login amb staff
        self.selenium.find_element(By.XPATH, '//button[text()="Log out"]').click()
        self.selenium.find_element(By.XPATH, '//a[@href="/admin/"]').click()

        username_input = self.selenium.find_element(By.NAME, "username")
        username_input.send_keys('staff')

        password_input = self.selenium.find_element(By.NAME, "password")
        password_input.send_keys('IOCEAC2m3')

        self.selenium.find_element(By.XPATH, '//input[@value="Log in"]').click()

        # Navegar a les Questions
        self.selenium.find_element(By.XPATH, '//a[@href="/admin/polls/question/"]').click()

        # Comprovar que NO pot crear Questions
        try:
            self.selenium.find_element(By.XPATH, '//a[@href="/admin/polls/question/add/"]')
            assert False, "Trobat botó Add question"
        except NoSuchElementException:
            pass

        # Entrar a una Question i comprovar que NO pot esborrar
        self.selenium.find_element(By.XPATH, '//a[@href="/admin/polls/question/1/change/"]').click()
        
        try:
            self.selenium.find_element(By.XPATH, '//a[@href="/admin/polls/question/1/delete/"]')
            assert False, "Trobat enllaç Delete"
        except NoSuchElementException:
            pass
