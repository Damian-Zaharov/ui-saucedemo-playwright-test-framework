import pytest
import allure
from config import Config
from pages.inventory_page import InventoryPage
from pages.product_page import ProductPage
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from data.credentials import Credentials
from pages.checkout_complete_page import CheckoutCompletePage


@allure.epic("Каталог товаров")
@allure.feature("Сохранение сессии")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.regression
def test_session_persists_after_reload(page):
    """Тест проверяет, что после перезагрузки страницы авторизация не слетает"""

    # Инициализируем страницу каталога
    inventory_page = InventoryPage(page)

    # Открываем каталог напрямую в обход формы логина (куки подставятся сами)
    inventory_page.open()

    # Убеждаемся, что мы успешно попали на страницу каталога
    inventory_page.verify_url(Config.INVENTORY_URL)

    # Выполняем перезагрузку страницы браузера
    inventory_page.reload_catalog()

    # 5. Проверяем, что после перезагрузки система не разлогинила нас и мы остались тут же
    inventory_page.verify_url(Config.INVENTORY_URL)


@allure.epic("Каталог товаров")
@allure.feature("Безопасность и ограничение доступа")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.regression
def test_access_denied_without_auth(browser):
    """Тест проверяет редирект и ошибку при попытке зайти в каталог без кук"""

    # Создаем изолированный контекст без кук и страницу в нем
    context = browser.new_context()
    page = context.new_page()

    # Инициализируем страницу каталога для этого чистого окна
    inventory_page = InventoryPage(page)

    # Пытаемся зайти в каталог напрямую
    inventory_page.open()

    # Проверяем, что нас перенаправило обратно на главную страницу (Base URL)
    inventory_page.verify_url(Config.BASE_URL)

    # Проверяем, что на странице отображается нужный текст ошибки
    inventory_page.verify_access_error_message()

    # Закрываем временный контекст
    context.close()


@allure.epic("Каталог товаров")
@allure.feature("Отображение контента")
@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.smoke
def test_all_products_display_correctly(page):
    """Тест проверяет корректность отображения всех карточек товаров в каталоге"""

    inventory_page = InventoryPage(page)

    # Заходим в каталог (куки подставятся автоматически)
    inventory_page.open()
    inventory_page.verify_url(Config.INVENTORY_URL)

    # Вызываем наш комплексный метод проверки данных
    inventory_page.verify_all_products_have_valid_data()


@allure.epic("Каталог товаров")
@allure.feature("Сортировка")
@allure.story("Сортировка по названию")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.regression
def test_product_sorting_by_name(page):
    """Тест проверяет работу фильтра сортировки товаров по имени"""

    inventory_page = InventoryPage(page)
    inventory_page.open()
    inventory_page.verify_url(Config.INVENTORY_URL)

    # Проверяем дефолтную сортировку от A до Z
    inventory_page.verify_sorting_by_name(direction="A-Z")

    # Переключаем фильтр на сортировку от Z до A (значение 'za' из HTML)
    inventory_page.select_sort_option(value="za")

    # Проверяем, что товары перестроились в обратном алфавитном порядке
    inventory_page.verify_sorting_by_name(direction="Z-A")


@allure.epic("Каталог товаров")
@allure.feature("Сортировка")
@allure.story("Сортировка по цене")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.regression
def test_product_sorting_by_price(page):
    """Тест проверяет работу фильтра сортировки товаров по цене"""

    inventory_page = InventoryPage(page)
    inventory_page.open()
    inventory_page.verify_url(Config.INVENTORY_URL)

    # Переключаем фильтр на сортировку от дешевых к дорогим (value="lohi" из HTML)
    inventory_page.select_sort_option(value="lohi")

    # Проверяем сортировку по возрастанию цены
    inventory_page.verify_sorting_by_price(direction="low-to-high")

    # Переключаем фильтр на сортировку от дорогих к дешевым (value="hilo" из HTML)
    inventory_page.select_sort_option(value="hilo")

    # Проверяем сортировку по убыванию цены
    inventory_page.verify_sorting_by_price(direction="high-to-low")


@allure.epic("Каталог товаров")
@allure.feature("Детальная страница товара")
@allure.story("Проверка цены товара")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.regression
def test_product_prices_match_on_detail_page(page):
    """Тест проверяет, что цена каждого товара в каталоге совпадает с ценой на его личной странице"""

    inventory_page = InventoryPage(page)
    product_page = ProductPage(page)

    inventory_page.open()
    inventory_page.verify_url(Config.INVENTORY_URL)

    # Получаем общее количество товаров (их 6)
    total_products = inventory_page.get_products_count()

    # Запускаем цикл по индексам от 0 до 5
    for i in range(total_products):
        with allure.step(f"Проверка консистентности цены для товара с индексом {i}"):
            # Запоминаем цену из каталога и заходим внутрь товара
            expected_price = inventory_page.click_product_by_index_and_get_price(i)

            # Находясь на странице товара, проверяем, что цена совпадает
            product_page.verify_product_price(expected_price)

            # Идём обратно в каталог
            inventory_page.open()


@allure.epic("Каталог товаров")
@allure.feature("Детальная страница товара")
@allure.story("Добавление и удаление товаров")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.smoke
def test_product_button_syncs_to_remove_state(page):
    """Тест проверяет, что после добавления товара на главной, кнопка внутри карточки тоже меняется на Remove"""

    inventory_page = InventoryPage(page)
    product_page = ProductPage(page)
    inventory_page.open()
    inventory_page.verify_url(Config.INVENTORY_URL)

    # Добавляем в корзину первый товар прямо из общего каталога
    inventory_page.add_product_to_cart_by_index(0)

    # Кликаем по названию этого же первого товара, чтобы перейти на его личную страницу
    inventory_page.click_product_by_index_and_get_price(0)

    # Находясь внутри карточки товара, проверяем, что кнопка синхронно стала "Remove"
    product_page.verify_button_is_in_remove_state()

    # Кликаем Remove
    product_page.detail_action_button.click()


@allure.epic("Каталог товаров")
@allure.feature("Оформление заказа")
@allure.story("Цикл добавления и удаления товара")
@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.smoke
def test_full_cart_workflow_e2e(page):
    """Сквозной тест: Добавление товара ➔ Проверка счетчика ➔ Валидация данных в корзине ➔ Удаление"""

    inventory_page = InventoryPage(page)
    cart_page = CartPage(page)

    inventory_page.open()
    inventory_page.verify_url(Config.INVENTORY_URL)

    # Запоминаем название и цену первого товара (индекс 0) для последующей сверки
    product_name, product_price = inventory_page.get_product_data_by_index(0)

    # Кликаем "Add to cart" на главной странице для этого товара
    inventory_page.add_product_to_cart_by_index(0)

    # Проверяем, что вверху сайта на значке корзины загорелась цифра 1
    # Метод из BasePage, поэтому зовём через объект любой страницы
    inventory_page.verify_cart_badge_count("1")

    # Переходим на страницу корзины кликом по иконке в хэдере
    inventory_page.click_cart_icon()

    # Проверяем, что товар внутри корзины содержит те же Title и Price
    cart_page.verify_product_in_cart(product_name, product_price)

    # Нажимаем кнопку Remove внутри корзины
    cart_page.remove_product_from_cart()

    # Проверяем, что счетчик вверху страницы полностью исчез (корзина пуста)
    cart_page.verify_cart_badge_is_hidden()


@allure.epic("Каталог товаров")
@allure.feature("Оформление заказа")
@allure.story("Валидация формы Checkout")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.regression
def test_checkout_first_name_validation(page):
    """Негативный тест: Проверка ошибки обязательности полей при оформлении заказа"""

    inventory_page = InventoryPage(page)
    cart_page = CartPage(page)
    checkout_page = CheckoutPage(page)

    # Заходим в каталог с куками
    inventory_page.open()
    inventory_page.verify_url(Config.INVENTORY_URL)

    # Добавляем последний товар в корзину
    inventory_page.add_last_product_to_cart()

    # Переходим в корзину
    inventory_page.click_cart_icon()

    # Нажимаем Checkout
    cart_page.click_checkout()

    # Нажимаем Continue на пустой форме
    checkout_page.click_continue()

    # Проверяем появление ошибки "Error: First Name is required"
    checkout_page.verify_first_name_required_error()


@allure.epic("Каталог товаров")
@allure.feature("Оформление заказа")
@allure.story("Успешный сквозной заказ (E2E)")
@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.smoke
def test_successful_purchase_workflow_e2e(page):
    """Сквозной тест покупки двух товаров с полной валидацией математики цен и переходов"""

    inventory_page = InventoryPage(page)
    cart_page = CartPage(page)
    checkout_page = CheckoutPage(page)
    complete_page = CheckoutCompletePage(page)

    inventory_page.open()
    inventory_page.verify_url(Config.INVENTORY_URL)

    # Запоминаем данные двух первых товаров (индексы 0 и 1)
    prod1_name, prod1_price = inventory_page.get_product_data_by_index(0)
    prod2_name, prod2_price = inventory_page.get_product_data_by_index(1)

    # Сохраняем их списком для удобной передачи в методы проверки
    expected_products = [(prod1_name, prod1_price), (prod2_name, prod2_price)]

    # Вычисляем ожидаемую чистую сумму для проверки
    sum_prices = float(prod1_price.replace("$", "")) + float(prod2_price.replace("$", ""))

    # Кликаем "Add to cart" для обоих товаров
    inventory_page.add_product_to_cart_by_index(0)
    inventory_page.add_product_to_cart_by_index(1)

    # Переходим в корзину и нажимаем Checkout
    inventory_page.click_cart_icon()
    cart_page.click_checkout()

    # Заполняем форму покупателя данными из redentials и жмем Continue
    checkout_page.fill_buyer_information(
        first_name=Credentials.BuyerData.FIRST_NAME,
        last_name=Credentials.BuyerData.LAST_NAME,
        zip_code=Credentials.BuyerData.ZIP_CODE
    )
    checkout_page.click_continue()

    # На этапе Overview проверяем соответствие Titles и Цен
    checkout_page.verify_overview_products(expected_products)

    # Проверяем равенство сумм и формулу "Item total + Tax == Total"
    checkout_page.verify_checkout_totals(expected_subtotal=sum_prices)

    # Завершаем заказ
    checkout_page.click_finish()

    # Проверяем, что попали на страницу завершения заказа
    complete_page.verify_url(Config.CHECKOUT_COMPLETE_URL)

    # Возвращаемся на главную и проверяем, что мы в каталоге
    complete_page.click_back_home()
    complete_page.verify_url(Config.INVENTORY_URL)