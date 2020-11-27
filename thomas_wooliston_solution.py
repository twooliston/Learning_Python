"""
Please write you name here: Thomas Wooliston
"""

import csv
from datetime import datetime, time, timedelta

def process_shifts(path_to_csv):
    """

    :param path_to_csv: The path to the work_shift.csv
    :type string:
    :return: A dictionary with time as key (string) with format %H:%M
        (e.g. "18:00") and cost as value (Number)
    For example, it should be something like :
    {
        "17:00": 50,
        "22:00: 40,
    }
    In other words, for the hour beginning at 17:00, labour cost was
    50 pounds
    :rtype dict:
    """

    processed_shifts = {}

    # read file
    with open(path_to_csv, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)

        # skip headers (could use in future to identifdy the data)
        next(csv_reader)

        for line in csv_reader:
            # get start and end time
            try:
                start_time = datetime.strptime(line[3], '%H:%M')
                end_time = datetime.strptime(line[1], '%H:%M')
            except ValueError:
                print("invalid time format")
                
            break_note = line[0]
            times_in_break_note = extract_time_from_notes(break_note)
            times_in_break_note_formatted = [format_time(x) for x in times_in_break_note]

            start_of_break_time = times_in_break_note_formatted[0]
            end_of_break_time = times_in_break_note_formatted[1]

            # process pre-break shift
            account_for_not_starting_on_the_hour = start_time
            if start_time.minute != 0:
                account_for_not_starting_on_the_hour += timedelta(hours=1)
            calculate_cost_per_hour_from_salaries(processed_shifts, account_for_not_starting_on_the_hour, start_of_break_time, line[2])

            # process post-break shift
            account_for_not_starting_on_the_hour = end_of_break_time
            if end_of_break_time.minute != 0:
                account_for_not_starting_on_the_hour += timedelta(hours=1)
            calculate_cost_per_hour_from_salaries(processed_shifts, account_for_not_starting_on_the_hour, end_time, line[2])

            # process leftover minutes: start of shift
            calculate_extra_minutes(processed_shifts, start_time, (start_time.minute / 60), line[2])

            # process leftover minutes: end of shift
            calculate_extra_minutes(processed_shifts, end_time, (1 - end_time.minute / 60), line[2])

            # process leftover minutes: start of break
            calculate_extra_minutes(processed_shifts, start_of_break_time, (start_of_break_time.minute / 60), line[2])

            # process leftover minutes: end of break
            calculate_extra_minutes(processed_shifts, end_of_break_time, (1 - end_of_break_time.minute / 60), line[2])

    return processed_shifts

def calculate_extra_minutes(processed_shifts, start, extra_time, pay_rate):
    if start.minute != 0:
        pay_rate_for_fraction_of_hour_worked = round(extra_time * float(pay_rate), 2)
        next_hour = start + timedelta(hours=1)
        calculate_cost_per_hour_from_salaries(processed_shifts, start, next_hour, pay_rate_for_fraction_of_hour_worked)
            
def extract_time_from_notes(time):
    # assuming there is always a '-' char separating the dates
    times_in_break_note = []

    index_of_time_separator = time.find('-')

    # if there is no '-'
    if index_of_time_separator == -1:
        print("invalid time format in break notes")

    # remove blank spaces
    start_of_break = time[:index_of_time_separator].strip()
    end_of_break = time[index_of_time_separator + 1 :].strip()

    # append to array to return
    times_in_break_note.append(start_of_break)
    times_in_break_note.append(end_of_break)
    
    return times_in_break_note

def format_time(time_string):
    formatted_time = ""
    find_time = ""

    # check if string hints at the time not being in 24h format
    needs_to_be_converted_to_24h = "PM" in time_string or "pm" in time_string
    
    # identify the times from the string
    for ch in time_string:
        if ch.isdigit():
            find_time += ch
        elif ch == '.' or ch == ':':
            find_time += ":"

    # add minutes if needed
    if find_time:
        if len(find_time) <= 2:
            find_time += ":00"

    formatted_time = datetime.strptime(find_time, '%H:%M')

    # convert to 24h (assuming the opening hour is 9am)
    if needs_to_be_converted_to_24h or formatted_time.time() < time(9,0):
        formatted_time += timedelta(hours=12)

    return formatted_time

def calculate_cost_per_hour_from_salaries(processed_shifts, start, end, pay_rate):
    for work_hour in range(start.hour, end.hour):
        work_hour_formatted = time(work_hour,0).strftime('%H:%M')

        # if exists, add to existing total
        # else create new key with new value
        if work_hour_formatted in processed_shifts:
            processed_shifts.update({work_hour_formatted: round(processed_shifts.get(work_hour_formatted) + float(pay_rate), 2)})
        else:
            processed_shifts.update({work_hour_formatted: float(pay_rate)})

def process_sales(path_to_csv):
    """

    :param path_to_csv: The path to the transactions.csv
    :type string:
    :return: A dictionary with time (string) with format %H:%M as key and
    sales as value (string),
    and corresponding value with format %H:%M (e.g. "18:00"),
    and type float)
    For example, it should be something like :
    {
        "17:00": 250,
        "22:00": 0,
    },
    This means, for the hour beginning at 17:00, the sales were 250 dollars
    and for the hour beginning at 22:00, the sales were 0.

    :rtype dict:
    """
    processed_sales = {}

    # read file
    with open(path_to_csv, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)

        # skip headers (could use in future to identifdy the data)
        next(csv_reader)

        for line in csv_reader:
            # create key based on the hour
            time = line[1][:2] + ":00"

            # if exists, add to existing total
            # else create new key with new value
            if time in processed_sales:
                processed_sales.update({time: round(processed_sales.get(time) + float(line[0]), 2)})
            else:
                processed_sales.update({time: float(line[0])})
                
    return processed_sales

def compute_percentage(shifts, sales):
    """

    :param shifts:
    :type shifts: dict
    :param sales:
    :type sales: dict
    :return: A dictionary with time as key (string) with format %H:%M and
    percentage of labour cost per sales as value (float),
    If the sales are null, then return -cost instead of percentage
    For example, it should be something like :
    {
        "17:00": 20,
        "22:00": -40,
    }
    :rtype: dict
    """
    computed_percentage = {}
    # assuming opening/closing times are constant otherwise a look up of earliest time and latest time is needed
    opening_time = 9
    closing_time = 23

    for work_hour in range(opening_time, closing_time):
        work_hour_formatted = time(work_hour,0).strftime('%H:%M')

        # check if there were shifts during the hour
        if work_hour_formatted in shifts:
            shift_cost = shifts.get(work_hour_formatted)
        else:
            shift_cost = 0

        # check if there were sales during the hour
        if work_hour_formatted in sales:
            sales_cost = sales.get(work_hour_formatted)
        else:
            sales_cost = 0

        # compute percentage or the cost of paying salaries
        if shift_cost == 0 :
            print(" no one working at: " + work_hour_formatted)
        elif sales_cost == 0:
            computed_percentage.update({work_hour_formatted: -1 * shift_cost})
        else:
            percentage = round((shift_cost/sales_cost)*100, 2)
            # to account for the issue raised in the "best_and_worst_hour(percentages)" function
            if percentage > 100:
                computed_percentage.update({work_hour_formatted: sales_cost - shift_cost})
            else :
                computed_percentage.update({work_hour_formatted: percentage})

    return computed_percentage

def best_and_worst_hour(percentages):
    """

    Args:
    percentages: output of compute_percentage
    Return: list of strings, the first element should be the best hour,
    the second (and last) element should be the worst hour. Hour are
    represented by string with format %H:%M
    e.g. ["18:00", "20:00"]

    """
    # there should be an issue: if there was more money paid into salaries than made in sales
    # there could be more money lost in those hours compared to hours where no sales were made
    # to calculate this, the money lost would need to be added to the function compute_percentage(shifts, sales)
    # my solution handles this issue

    worst, best = 0, 100

    # logic:
    # the best hour is the closest positive number to 0
    # worst hour is the lowest number (<0) or if there are no negatives, the highest percentage 
    for key in percentages:
        if worst < 0:
            if percentages[key] < worst:
                worst = percentages[key]
        else:
            if percentages[key] > worst or percentages[key] < 0:
                worst = percentages[key]
        if percentages[key] >= 0 and percentages[key] < 100:
            if percentages[key] < best:
                best = percentages[key]

    return [best, worst]

def main(path_to_shifts, path_to_sales):
    """
    Do not touch this function, but you can look at it, to have an idea of
    how your data should interact with each other
    """

    shifts_processed = process_shifts(path_to_shifts)
    sales_processed = process_sales(path_to_sales)
    print(sales_processed)
    percentages = compute_percentage(shifts_processed, sales_processed)
    best_hour, worst_hour = best_and_worst_hour(percentages)
    return best_hour, worst_hour

if __name__ == '__main__':
    # You can change this to test your code, it will not be used
    path_to_sales = "transactions.csv"
    path_to_shifts = "work_shifts.csv"
    best_hour, worst_hour = main(path_to_shifts, path_to_sales)


# Please write you name here: Thomas Wooliston
