import statistics

class calculations:
    def __init__(self, std_dev, avg, median, length, min_val, max_val):
        self.std_dev = std_dev
        self.avg = avg
        self.median = median
        self.length = length
        self.min = min_val
        self.max = max_val

## Calculation functions:

def calc_standard_deviation(data):
    if len(data) <2:
        return 0
    return statistics.stdev(data)

def calc_avg(data):
    if len(data) <2:
        return 0
    return statistics.mean(data)

def calc_median(data):
    if len(data) <2:
        return 0
    return statistics.median(data)

def calc_length(data):
    if len(data) <2:
        return 0
    return len(data)


def calc_pipeline(data):
    std_dev = calc_standard_deviation(data)
    avg = calc_avg(data)
    median = calc_median(data)
    length = calc_length(data)
    min_val = min(data) if data else None
    max_val = max(data) if data else None
    return calculations(std_dev, avg, median, length, min_val, max_val)


