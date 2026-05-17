import allure
from pages.base_page import BasePage
from playwright.sync_api import Page, expect


class CartPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        # Локатор единственного (или первого) товара в корзине
        self.cart_item = page.locator('[data-test="inventory-item"]')

        # Относительные локаторы внутри элемента корзины
        self.item_name = '[data-test="inventory-item-name"]'
        self.item_price = '[data-test="inventory-item-price"]'
        self.remove_button = 'button.cart_button'  # Универсальный селектор кнопки Remove

    # Метод валидации данных товара внутри корзины
    @allure.step("Проверить, что в корзине лежит товар с названием '{expected_name}' и ценой '{expected_price}'")
    def verify_product_in_cart(self, expected_name: str, expected_price: str):
        """Проверяет, что первый элемент в корзине соответствует сохраненным данным"""
        expect(self.cart_item).to_be_visible()

        # Сверяем имя товара
        expect(self.cart_item.locator(self.item_name)).to_have_text(expected_name)
        # Сверяем цену товара
        expect(self.cart_item.locator(self.item_price)).to_have_text(expected_price)

    # Метод нажатия кнопки Remove на странице корзины
    @allure.step("Нажать кнопку 'Remove' внутри корзины")
    def remove_product_from_cart(self):
        """Удаляет товар и проверяет, что карточка товара исчезла из списка корзины"""
        self.cart_item.locator(self.remove_button).click()
        # Проверяем, что контейнер товара полностью пропал из корзины
        expect(self.cart_item).to_be_hidden()


    def __init__(self, page: Page):
        super().__init__(page)
        self.cart_item = page.locator('[data-test="inventory-item"]')
        self.item_name = '[data-test="inventory-item-name"]'
        self.item_price = '[data-test="inventory-item-price"]'
        self.remove_button = 'button.cart_button'

        # Локатор кнопки Checkout на странице корзины
        self.checkout_button = page.locator('[data-test="checkout"]')

    # Метод для перехода к оформлению заказа
    @allure.step("Нажать кнопку 'Checkout' в корзине")
    def click_checkout(self):
        """Кликает по кнопке Checkout для перехода на страницу ввода данных"""
        self.checkout_button.click()
