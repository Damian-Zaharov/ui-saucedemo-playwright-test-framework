import allure
from pages.base_page import BasePage
from playwright.sync_api import Page, expect

class CheckoutPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        # Локатор кнопки продолжения оформления
        self.continue_button = page.locator('[data-test="continue"]')
        # Локатор контейнера с ошибкой валидации формы
        self.error_container = page.locator('[data-test="error"]')

        # Локаторы полей ввода данных покупателя
        self.first_name_input = page.locator('[data-test="firstName"]')
        self.last_name_input = page.locator('[data-test="lastName"]')
        self.postal_code_input = page.locator('[data-test="postalCode"]')

        # Локаторы для второго шага (Checkout: Overview) ---
        self.cart_items = page.locator('[data-test="inventory-item"]')
        self.item_name = '[data-test="inventory-item-name"]'
        self.item_price = '[data-test="inventory-item-price"]'

        # Локаторы итоговых цен внизу страницы
        self.item_total_label = page.locator('[data-test="subtotal-label"]')
        self.tax_label = page.locator('[data-test="tax-label"]')
        self.total_label = page.locator('[data-test="total-label"]')

        self.finish_button = page.locator('[data-test="finish"]')



    @allure.step("Нажать кнопку 'Continue' на странице Checkout")
    def click_continue(self):
        """Нажимает продолжить без заполнения полей, чтобы вызвать ошибку"""
        self.continue_button.click()

    @allure.step("Проверить, что отображается ошибка: 'Error: First Name is required'")
    def verify_first_name_required_error(self):
        """Проверяет видимость плашки и точный текст ошибки обязательного поля Имени"""
        expected_error = "Error: First Name is required"
        expect(self.error_container).to_be_visible()
        expect(self.error_container).to_have_text(expected_error)

    @allure.step("Заполнить форму покупателя данными: {first_name}, {last_name}, {zip_code}")
    def fill_buyer_information(self, first_name: str, last_name: str, zip_code: str):
        """Вводит персональные данные в поля формы"""
        self.first_name_input.fill(first_name)
        self.last_name_input.fill(last_name)
        self.postal_code_input.fill(zip_code)

    @allure.step("Проверить, что список товаров на этапе Overview совпадает с ожидаемым")
    def verify_overview_products(self, expected_products: list[tuple[str, str]]):
        """Проверяет соответствие названий и цен для всех добавленных товаров в списке"""
        items_list = self.cart_items.all()
        assert len(items_list) == len(expected_products), "Количество товаров в Overview не совпадает с добавленным!"

        for index, item in enumerate(items_list):
            exp_name, exp_price = expected_products[index]
            expect(item.locator(self.item_name)).to_have_text(exp_name)
            expect(item.locator(self.item_price)).to_have_text(exp_price)

    @allure.step("Проверить математический расчет итоговой стоимости и налогов в UI")
    def verify_checkout_totals(self, expected_subtotal: float):
        """
        Парсит строки цен из UI, проверяет равенство Item Total сумме цен,
        а также корректность формулы Total == Item Total + Tax.
        """
        # 1. Извлекаем числа из строк UI (например, "Item total: $39.98" -> 39.98)
        ui_subtotal_text = self.item_total_label.text_content()
        ui_subtotal = float(ui_subtotal_text.split("$")[1])

        ui_tax_text = self.tax_label.text_content()
        ui_tax = float(ui_tax_text.split("$")[1])

        ui_total_text = self.total_label.text_content()
        ui_total = float(ui_total_text.split("$")[1])

        # Проверяем цены
        assert ui_subtotal == expected_subtotal, (f"Сумма товаров в UI ({ui_subtotal}) "
                                                  f"не равна ожидаемой ({expected_subtotal})!")

        expected_calculated_total = round(ui_subtotal + ui_tax, 2)
        assert ui_total == expected_calculated_total, (f"Общий итог в UI ({ui_total}) "
                                                       f"не равен Item Total + Tax ({expected_calculated_total})!")

    @allure.step("Нажать кнопку 'Finish' для подтверждения заказа")
    def click_finish(self):
        """Нажимает финиш для завершения транзакции"""
        self.finish_button.click()