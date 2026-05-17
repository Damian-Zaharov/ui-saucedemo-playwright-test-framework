import allure
from pages.base_page import BasePage
from playwright.sync_api import Page, expect

class ProductPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)

        # Локатор цены на детальной странице товара
        self.detail_price = page.locator('[data-test="inventory-item-price"]')
        # Кнопка возврата к списку "Back to products"
        self.back_button = page.locator('[data-test="back-to-products"]')
        # Универсальный локатор кнопки действия на детальной странице товара
        self.detail_action_button = page.locator("button.btn_inventory")

    @allure.step("Проверить, что цена товара на детальной странице равна '{expected_price}'")
    def verify_product_price(self, expected_price: str):
        """Проверяет точное совпадение цены на странице товара с переданным значением"""
        expect(self.detail_price).to_have_text(expected_price)

    @allure.step("Проверить, что на странице товара кнопка находится в состоянии 'Remove'")
    def verify_button_is_in_remove_state(self):
        """Убеждается, что кнопка синхронизировалась и показывает текст Remove"""
        expect(self.detail_action_button).to_have_text("Remove")