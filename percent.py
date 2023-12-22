def percentage(part, whole):
    if whole == 0:
        return 0
    part = part / 100
    percent = part * whole
    return percent

def percentage_diff(num2, num1):
    return ((float(num1) - float(num2)) / float(num2)) * 100
