
def get_totalgross_value(total_gross) :
    if total_gross != total_gross :
        return total_gross

    return float(total_gross.replace('$', '').replace(',', ''))