from decimal import Decimal
from django.utils.translation import gettext_lazy as _

class TaxCalculator:
    """
    Утилітний клас для обчислення податків для корзини/замовлення
    """

    @staticmethod
    def calculate_cart_taxes(cart_items):
        """
        Обчислює податки для списку товарів у корзині

        Args:
            cart_items: Список, де кожен елемент - словник з ключами:
                - product: об'єкт Product
                - quantity: кількість
                - price: ціна за одиницю (опціонально, інакше використовується base_price)

        Returns:
            tuple: (total_net, taxes_dict, total_gross)
                - total_net: загальна сума без податків
                - taxes_dict: словник {tax_name: tax_amount}
                - total_gross: загальна сума з податками
        """
        total_net = Decimal('0.00')
        taxes = {}

        for item in cart_items:
            product = item['product']
            quantity = item['quantity']
            price = item.get('price', product.base_price)

            # Обчислюємо суму без податків
            item_total = price * quantity
            total_net += item_total

            if product.taxable:
                # Обчислюємо податки для продукту
                product_taxes = product.calculate_taxes(quantity=quantity)

                # Додаємо податки до загального словника
                for tax_name, amount in product_taxes.items():
                    if tax_name in taxes:
                        taxes[tax_name] += amount
                    else:
                        taxes[tax_name] = amount

        # Обчислюємо загальну суму з податками
        total_tax = sum(taxes.values())
        total_gross = total_net + total_tax

        return total_net, taxes, total_gross

    @staticmethod
    def format_tax_summary(taxes_dict, total_net, total_gross):
        """
        Форматує підсумок податків для відображення

        Args:
            taxes_dict: словник {tax_name: tax_amount}
            total_net: загальна сума без податків
            total_gross: загальна сума з податками

        Returns:
            str: Відформатований підсумок податків
        """
        summary = [f"{_('Сума без податків')}: {total_net:.2f} грн"]

        for tax_name, amount in taxes_dict.items():
            summary.append(f"{tax_name}: {amount:.2f} грн")

        summary.append(f"{_('Загальна сума з податками')}: {total_gross:.2f} грн")

        return "\n".join(summary)


def get_product_type_tax_code(product_type):
    """
    Повертає код типу податку, який відповідає типу продукту

    Args:
        product_type: Тип продукту (наприклад, 'food', 'tobacco')

    Returns:
        str: Код типу податку або None, якщо немає відповідності
    """
    # Маппінг типів продуктів на коди податків
    mapping = {
        'food': 'vat_reduced',
        'tobacco': 'excise_tobacco',
        'alcohol': 'excise_alcohol',
        'industrial': 'vat_standard',
        'electronics': 'vat_standard',
        'clothing': 'vat_standard',
    }

    return mapping.get(product_type)


def calculate_vat(price, rate=20):
    """
    Обчислює ПДВ за заданою ставкою

    Args:
        price: Ціна без податку
        rate: Ставка ПДВ у відсотках (за замовчуванням 20%)

    Returns:
        Decimal: Сума ПДВ
    """
    return Decimal(price) * Decimal(rate) / Decimal(100)


def calculate_excise_tobacco(price, quantity, fixed_amount=19.00, ad_valorem_rate=12):
    """
    Обчислює акцизний податок на тютюнові вироби

    Args:
        price: Ціна за одиницю
        quantity: Кількість (пачок)
        fixed_amount: Фіксована сума за пачку (грн)
        ad_valorem_rate: Відсоток від вартості (%)

    Returns:
        Decimal: Сума акцизного податку
    """
    fixed_part = Decimal(fixed_amount) * quantity
    ad_valorem_part = Decimal(price) * quantity * Decimal(ad_valorem_rate) / Decimal(100)
    return fixed_part + ad_valorem_part
