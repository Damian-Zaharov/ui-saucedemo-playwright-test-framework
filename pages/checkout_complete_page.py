import allure
from pages.base_page import BasePage
from playwright.sync_api import Page

class CheckoutCompletePage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        # Локатор кнопки возврата на главную страницу каталога
        self.back_home_button = page.locator('[data-test="back-to-products"]')

    @allure.step("Нажать кнопку 'Back Home' на экране завершения заказа")
    def click_back_home(self):
        """Кликает по кнопке возврата"""
        self.back_home_button.click()
