def receipt_line(item: str, quantity: int, unit_price: float) -> str:
    """Return one line of a receipt, like "3 x apple @ $0.50 = $1.50".

    Prices always show two decimal places.
    """
    total = quantity * unit_price
    return f"{quantity} x {item} @ ${unit_price:.2f} = ${total:.2f}"
