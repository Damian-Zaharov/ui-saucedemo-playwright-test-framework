import pytest
import os
from filelock import FileLock
from playwright.sync_api import Browser, BrowserContext, Page
from pages.login_page import LoginPage
from config import Config

# Здесь будут куки для последующих тестов
AUTH_FILE_NAME = "auth_state.json"


@pytest.fixture(scope="session")
def global_auth_file_path(tmp_path_factory, worker_id) -> str:
    """Вспомогательная фикстура, которая вычисляет путь к файлу auth_state.json для всех потоков"""
    if worker_id == "master":
        # При одиночном запуске храним файл просто в корне проекта
        return AUTH_FILE_NAME

    # При параллельном запуске берем общую директорию верхнего уровня pytest
    root_tmp_dir = tmp_path_factory.getbasetemp().parent
    return str(root_tmp_dir / AUTH_FILE_NAME)


@pytest.fixture(scope="session", autouse=True)
def session_auth(browser: Browser, tmp_path_factory, worker_id, global_auth_file_path):
    """Фикстура авторизации. Создает файл кук в общей папке
    и заставляет другие потоки ждать окончания процесса через FileLock"""
    if worker_id == "master":
        _create_auth_state(browser, global_auth_file_path)
        return

    # Папка для файла блокировки
    root_tmp_dir = tmp_path_factory.getbasetemp().parent
    lock_file = root_tmp_dir / "auth.lock"

    # Блокируем проход для всех потоков, кроме первого
    with FileLock(str(lock_file), timeout=60): # Если логин не прошёл за 60 сек - остальные тесты выкинут TimeoutError,
        # завершатся false, и не будут тратить бесплатные минуты сборки

        # Если первый поток еще не создал файл по общему пути — создаем
        if not os.path.exists(global_auth_file_path):
            _create_auth_state(browser, global_auth_file_path)


@pytest.fixture(scope="function")
def context(browser: Browser, global_auth_file_path):
    """Каждый тест создает контекст, подтягивая куки из гарантированно
    существующего общего файла global_auth_file_path"""
    if os.path.exists(global_auth_file_path):
        print(f"\n[WORKER] Подгружаем куки из: {global_auth_file_path}")
        context = browser.new_context(storage_state=global_auth_file_path)
    else:
        print("\n[WORKER] Файл авторизации не найден! Запуск в пустом контексте.")
        context = browser.new_context()

    yield context
    context.close()


@pytest.fixture(scope="function")
def login_page(browser: Browser) -> LoginPage:
    """Для тестов самого логина (и негативных тестов) всегда создаем чистый контекст - без кук"""
    context = browser.new_context() # Чистый контекст
    page = context.new_page()
    page_object = LoginPage(page)
    page_object.open()
    return page_object


def _create_auth_state(browser: Browser, file_path: str):
    """Генерирует сессию авторизации и сохраняет её по заданному пути"""
    if os.path.exists(file_path):
        os.remove(file_path)

    print(f"\n[AUTH MAIN] Инициализация сессии. Файл будет сохранен в: {file_path}")
    context = browser.new_context()
    page = context.new_page()

    login_page = LoginPage(page)
    login_page.open()
    login_page.login()
    login_page.verify_url(Config.INVENTORY_URL)

    # Сохраняем строго по переданному пути (в общую папку для xdist)
    context.storage_state(path=file_path)
    context.close()
    print("[AUTH MAIN] Авторизация успешно завершена")


def pytest_collection_modifyitems(config, items):
    """Сортировка запуска: тесты логина всегда в приоритете"""
    login_tests = []
    other_tests = []
    for item in items:
        if "login" in item.nodeid:
            login_tests.append(item)
        else:
            other_tests.append(item)
    items[:] = login_tests + other_tests
