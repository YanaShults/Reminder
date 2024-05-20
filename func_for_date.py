import datetime
import json_date
from dateutil.relativedelta import relativedelta


def date(year=datetime.datetime.now().year, month=datetime.datetime.now().month):
    date = datetime.datetime(year, month, 1)
    # json_date.replace_date(date)
    return date


def next_month():
    today = json_date.read_date()
    next_month_date = today + relativedelta(months=1)
    next_year = next_month_date.year
    next_month = next_month_date.month
    return date(year=next_year, month=next_month)


def prev_month():
    today = json_date.read_date()
    # print(today)
    prev_month_date = today - relativedelta(months=1)
    prev_year = prev_month_date.year
    prev_month = prev_month_date.month
    return date(year=prev_year, month=prev_month)

