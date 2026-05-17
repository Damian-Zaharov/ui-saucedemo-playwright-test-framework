import allure
from pages.base_page import BasePage
from data.credentials import Credentials
from config import Config
from playwright.sync_api import Page, expect


class LoginPage(BasePage):
    def __init__(self, page: Page):
        # Инициализируем BasePage
        super().__init__(page)

        # URL страницы логина
        self.url = Config.BASE_URL

        # Локаторы элементов страницы
        self.username_input = page.locator('[data-test="username"]')
        self.password_input = page.locator('[data-test="password"]')
        self.login_button = page.locator('[data-test="login-button"]')
        self.error_container = page.locator('[data-test="error"]')

    @allure.step("Открыть страницу авторизации")
    def open(self):
        """Открывает страницу авторизации"""
        self.visit(self.url)

    @allure.step("Выполнить вход в систему под пользователем '{username}'")
    def login(self, username: str = Credentials.VALID_USER, password: str = Credentials.VALID_PASSWORD):
        """Выполняет вход в систему c учётными данными из credentials"""
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.login_button.click()

    @allure.step("Проверить, что отображается сообщение об ошибке")
    def verify_error_message_is_visible(self):
        """Проверяет, что элемент ошибки отображается на странице"""
        expect(self.error_container).to_be_visible()

    @allure.step("Проверить, что сессионные куки успешно созданы после авторизации")
    def verify_session_cookies_present(self):
        """Проверяет, что в текущей сессии появились куки авторизации"""
        session_state = self.get_session_state()
        # Проверяем куки
        assert len(session_state['cookies']) > 0, "Список кук пуст после авторизации!"

