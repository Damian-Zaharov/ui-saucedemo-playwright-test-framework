import allure
from pages.base_page import BasePage
from config import Config
from playwright.sync_api import Page, expect
import re


class InventoryPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)

        # URL страницы каталога
        self.url = Config.INVENTORY_URL

        # Локатор ошибки доступа на странице инвентаря
        self.access_error_container = page.locator('[data-test="error"]')

        # Главный локатор для всех карточек товаров
        self.product_cards = page.locator('[data-test="inventory-item"]')

        # Относительные локаторы внутри каждой карточки
        self.product_name = '[data-test="inventory-item-name"]'
        self.product_price = '[data-test="inventory-item-price"]'
        self.product_image = '.inventory_item_img img'

        # Локатор для выпадающего списка сортировки
        self.sort_dropdown = page.locator('[data-test="product-sort-container"]')

        # Локатор кнопки добавления/удаления внутри карточки товара
        self.card_action_button = "button.btn_inventory"

    @allure.step("Открыть страницу каталога товаров напрямую")
    def open(self):
        """Открывает страницу каталога (работает, только если подложены куки)"""
        self.visit(self.url)

    @allure.step("Перезагрузить страницу каталога")
    def reload_catalog(self):
        """Выполняет перезагрузку текущей страницы"""
        self.page.reload()

    @allure.step("Проверить, что отображается ошибка отсутствия авторизации")
    def verify_access_error_message(self):
        """Проверяет видимость ошибки и её точный текст"""
        expected_text = "Epic sadface: You can only access '/inventory.html' when you are logged in."

        # Проверяем и видимость и текст внутри элемента
        expect(self.access_error_container).to_have_text(expected_text)

    # Метод валидации всех карточек товаров в каталоге
    @allure.step("Убедиться, что все товары на странице содержат корректные Title, Price и Image")
    def verify_all_products_have_valid_data(self):
        """Проверяет каждую карточку товара на наличие валидного имени, цены и картинки"""

        # Проверяем, что карточек больше нуля
        cards_count = self.product_cards.count()
        assert cards_count > 0, "На странице не найдено ни одной карточки товара!"

        # Соответствие формата цены (например, $29.99)
        price_pattern = re.compile(f"^\\$\\d+\\.\\d{{2}}$")

        # 2. Превращаем коллекцию локаторов в список для итерации через .all()
        cards_list = self.product_cards.all()

        for index, card in enumerate(cards_list, start=1):
            with allure.step(f"Валидация карточки товара №{index}"):
                # Находим элементы относительно текущей карточки
                name_locator = card.locator(self.product_name)
                price_locator = card.locator(self.product_price)
                image_locator = card.locator(self.product_image)

                # Проверка Title
                expect(name_locator).to_be_visible()
                name_text = name_locator.text_content().strip()
                assert len(name_text) > 0, f"У товара №{index} пустое название!"

                # Проверка Price
                expect(price_locator).to_be_visible()
                price_text = price_locator.text_content().strip()
                assert len(price_text) > 0, f"У товара №{index} отсутствует цена!"
                assert price_pattern.match(
                    price_text), f"Цена '{price_text}' товара №{index} не соответствует формату $XX.XX!"

                # Проверка Image
                expect(image_locator).to_be_visible()
                src_value = image_locator.get_attribute("src")

                assert src_value is not None, f"У товара №{index} отсутствует атрибут src!"
                assert len(src_value.strip()) > 0, f"У товара №{index} пустой путь к картинке!"
                # Защита от битых заглушек
                assert "WithGarbageOnIt" not in src_value, (f"У товара №{index} "
                                                            f"обнаружена битая картинка-заглушка! Src: {src_value}")

    # Метод для сбора всех названий товаров со страницы
    def get_all_product_names(self) -> list[str]:
        """Собирает и возвращает список названий всех товаров на странице"""
        cards_list = self.product_cards.all()
        names = []
        for card in cards_list:
            name_text = card.locator(self.product_name).text_content().strip()
            names.append(name_text)
        return names

    # Метод выбора сортировки
    @allure.step("Выбрать тип сортировки по значению '{value}'")
    def select_sort_option(self, value: str):
        """Выбирает опцию в выпадающем списке по её атрибуту value ('az', 'za', 'lohi', 'hilo')"""
        self.sort_dropdown.select_option(value=value)

    # Метод проверки сортировки по алфавиту
    @allure.step("Проверить, что товары отсортированы по алфавиту в направлении {direction}")
    def verify_sorting_by_name(self, direction: str = "A-Z"):
        """Проверяет правильность сортировки строк на странице каталога"""
        actual_names = self.get_all_product_names()

        if direction == "A-Z":
            # Сравниваем текущий список с отсортированным по возрастанию
            expected_names = sorted(actual_names)
            assert actual_names == expected_names, (f"Сортировка A-Z нарушена! "
                                                    f"Ожидалось: {expected_names}, Но получили: {actual_names}")
        elif direction == "Z-A":
            # Сравниваем текущий список с отсортированным по убыванию
            expected_names = sorted(actual_names, reverse=True)
            assert actual_names == expected_names, (f"Сортировка Z-A нарушена! "
                                                    f"Ожидалось: {expected_names}, Но получили: {actual_names}")

    # Метод для сбора цен всех товаров и конвертации их во float
    def get_all_product_prices(self) -> list[float]:
        """Собирает список цен всех товаров на странице и переводит их во float"""
        cards_list = self.product_cards.all()
        prices = []
        for card in cards_list:
            price_text = card.locator(self.product_price).text_content().strip()
            # Очищаем строку от знака $ и конвертируем во float
            clean_price = float(price_text.replace("$", ""))
            prices.append(clean_price)
        return prices

    # Метод проверки сортировки по цене
    @allure.step("Проверить, что товары отсортированы по цене в направлении {direction}")
    def verify_sorting_by_price(self, direction: str = "low-to-high"):
        """Проверяет правильность числовой сортировки цен на странице каталога"""
        actual_prices = self.get_all_product_prices()

        if direction == "low-to-high":
            # По возрастанию
            expected_prices = sorted(actual_prices)
            assert actual_prices == expected_prices, (f"Сортировка цен 'от дешевых к дорогим' нарушена! "
                                                      f"Ожидалось: {expected_prices}, Но получили: {actual_prices}")
        elif direction == "high-to-low":
            # По убыванию
            expected_prices = sorted(actual_prices, reverse=True)
            assert actual_prices == expected_prices, (f"Сортировка цен 'от дорогих к дешевым' нарушена! "
                                                      f"Ожидалось: {expected_prices}, Но получили: {actual_prices}")

    # Метод для получения общего количества карточек на странице
    def get_products_count(self) -> int:
        """Возвращает количество карточек товаров на странице"""
        return self.product_cards.count()

    # Метод для перехода на страницу товара по индексу с возвратом его цены
    @allure.step("Запомнить цену товара №{index} и кликнуть по его названию")
    def click_product_by_index_and_get_price(self, index: int) -> str:
        """Берет карточку по индексу (.nth), сохраняет её цену как текст и кликает по названию"""
        # .nth(index) берём элемент из коллекции по порядковому номеру начиная с 0
        target_card = self.product_cards.nth(index)

        # Запоминаем цену из карточки
        catalog_price = target_card.locator(self.product_price).text_content().strip()

        # Кликаем по названию для перехода
        target_card.locator(self.product_name).click()

        # Возвращаем строку с ценой, чтобы передать её дальше
        return catalog_price

    # Метод для добавления товара в корзину с главной страницы по индексу
    @allure.step("Нажать кнопку добавления в корзину у товара №{index}")
    def add_product_to_cart_by_index(self, index: int):
        """Находит карточку по индексу и кликает по её кнопке Add to cart"""
        target_card = self.product_cards.nth(index)
        button = target_card.locator(self.card_action_button)

        # Проверяем, что кнопка сейчас "Add to cart", и кликаем
        expect(button).to_have_text("Add to cart")
        button.click()

        # Проверяем, что состояние кнопки на главной - "Remove"
        expect(button).to_have_text("Remove")

    # Метод для получения и имени, и цены товара по его индексу
    def get_product_data_by_index(self, index: int) -> tuple[str, str]:
        """Возвращает кортеж (Название, Цена) для товара с указанным индексом"""
        target_card = self.product_cards.nth(index)
        name = target_card.locator(self.product_name).text_content().strip()
        price = target_card.locator(self.product_price).text_content().strip()
        return name, price

    @allure.step("Добавить последний товар из каталога в корзину")
    def add_last_product_to_cart(self):
        """Находит последнюю карточку товара через .nth(-1) и кликает Add to cart"""
        # -1 это последний элемент
        last_card = self.product_cards.nth(-1)
        button = last_card.locator(self.card_action_button)
        button.click()
