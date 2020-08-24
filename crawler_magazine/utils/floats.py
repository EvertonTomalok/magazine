def float_to_decimal(f: float):
    """
    This function is necessary because python transform float like
    2.0 in '2.00'
    """
    return "{:.2f}".format(f)
