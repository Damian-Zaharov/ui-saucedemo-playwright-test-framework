class Credentials:
    # Валидный пользователь
    VALID_USER = "standard_user"
    VALID_PASSWORD = "secret_sauce"

    # Невалидный пользователь
    INVALID_USER = "locked_out_user"
    INVALID_PASSWORD = "wrong_password"

    # Данные для заполнения полей оформления заказа
    class BuyerData:
        FIRST_NAME = "Иван"
        LAST_NAME = "Петров"
        ZIP_CODE = "12345"