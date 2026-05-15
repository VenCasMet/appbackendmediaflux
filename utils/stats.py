def calculate_reduction(original_size, converted_size):

    reduction = original_size - converted_size

    percent = 0

    if original_size > 0:

        percent = (reduction / original_size) * 100

    return reduction, round(percent, 2)