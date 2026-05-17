import allure
from playwright.sync_api import Page, expect
import re


class BasePage:
    def __init__(self, page: Page):
        self.page = page

        # Локатор иконки-счетчика корзины в верхнем меню
        self.cart_badge = page.locator('[data-test="shopping-cart-badge"]')

        # Локатор кнопки перехода в саму корзину (тележка)
        self.cart_link = page.locator('[data-test="shopping-cart-link"]')

    @allure.step("Открыть URL: {url}")
    def visit(self, url: str):
        """Открывает указанный URL"""
        return self.page.goto(url)

    @allure.step("Проверить, что текущий URL равен {expected_url}")
    def verify_url(self, expected_url: str):
        """Проверяет, что текущий URL соответствует ожидаемому (с ожиданием)"""
        # Убираем слэш из конца ожидаемой строки, если он есть
        clean_url = expected_url.rstrip('/')

        # Формируем строгое регулярное выражение
        strict_regex = re.compile(f"^{re.escape(clean_url)}/?$")

        expect(self.page).to_have_url(strict_regex)

    @allure.step("Получить состояние текущей сессии (куки и storage)")
    def get_session_state(self) -> dict:
        """Получить все куки, localStorage и sessionStorage текущей сессии"""
        return self.page.context.storage_state()

    @allure.step("Проверить, что на иконке корзины отображается цифра '{expected_count}'")
    def verify_cart_badge_count(self, expected_count: str):
        """Проверяет точное число на красном кружке корзины"""
        expect(self.cart_badge).to_have_text(expected_count)

    # Метод проверки, что счетчик корзины пуст (исчез)
    @allure.step("Проверить, что иконка счетчика корзины отсутствует (корзина пуста)")
    def verify_cart_badge_is_hidden(self):
        """Когда корзина пуста, Saucedemo полностью скрывает тег span со счетчиком"""
        expect(self.cart_badge).to_be_hidden()

    @allure.step("Кликнуть по иконке корзины и перейти на страницу корзины")
    def click_cart_icon(self):
        """Нажимает на тележку вверху экрана"""
        self.cart_link.click()
