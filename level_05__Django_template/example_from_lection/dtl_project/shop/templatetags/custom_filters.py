from django import template

register = template.Library()

CURRENCY_SYMBOLS = {
    'usd': '$',
    'euro': '€',
    'rub': '₽',
}


@register.filter(name='currency_format')
def currency_format(value, currency=None):
    """
    Форматирует число в денежный формат с указанием валюты.
    Пример:
        {{ 123456.78|currency_format:"usd" }} → $123 456,78
        {{ 123456.78|currency_format }} → 123 456,78 ₽
    """
    try:
        value = float(value)
    except (TypeError, ValueError):
        return ''

    formatted = f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", " ")

    currency = (currency or '').lower()
    symbol = CURRENCY_SYMBOLS.get(currency)

    if symbol:
        return f"{symbol}{formatted}"  # Валюта указана — символ в начале
    else:
        return f"{formatted} ₽"  # По умолчанию — рубль в конце