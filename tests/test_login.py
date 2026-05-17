import allure
import pytest
from config import Config
from pages.login_page import LoginPage
from data.credentials import Credentials


@allure.epic("Авторизация")
@allure.feature("Успешный вход в систему")
@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.smoke
def test_successful_login(login_page: LoginPage):
    """Тест успешной авторизации с валидными данными"""

    # Выполняем логин
    login_page.login()

    # Проверяем успешный редирект на страницу каталога
    login_page.verify_url(Config.INVENTORY_URL)

    # Получаем состояние сессии (куки, localStorage)
    session_state = login_page.get_session_state()

    # Проверяем что куки не пустые
    login_page.verify_session_cookies_present()


@allure.epic("Авторизация")
@allure.feature("Вход с невалидными данными")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.regression
@pytest.mark.order()
def test_login_with_invalid_credentials(login_page: LoginPage):
    """Тест проверки ошибки при вводе неверного логина и пароля"""

    # Передаем невалидные данные из нашего файла credentials.py
    login_page.login(
        username=Credentials.INVALID_USER,
        password=Credentials.INVALID_PASSWORD
    )

    # Проверяем что мы остались на BASE_URL
    login_page.verify_url(Config.BASE_URL)

    # ШПроверяем что появилась "ошибка"
    login_page.verify_error_message_is_visible()
