# import packages required
import matplotlib.pyplot as plt

from db import *

def plotByDateBar():
    sum_by_date = sum_by_day()
    left = []
    tick_label = []
    height = []
    i = 0
    for record in sum_by_date:
        i += 1
        tick_label.append(record["_id"][6:]+"/"+record["_id"][:4:7]+"/"+record['_id'][:4:])
        height.append(record["total"])
        left.append(i)

    plt.xlabel('Date')
    plt.ylabel('Expenses')
    plt.title('Expenses by Day')
    plt.bar(left, height, tick_label=tick_label, width=0.8, color=['red', 'green'])
    plt.show()

def plotByCategoryBar():
    sum_by_cat = sum_by_category()
    left = []
    tick_label = []
    height = []
    i = 0
    for record in sum_by_cat:
        i+=1
        tick_label.append(record['_id'])
        height.append(record['total'])
        left.append(i)

    plt.xlabel('Category')
    plt.ylabel('Expenses')
    plt.title('Expenses by Category ')
    plt.bar(left, height, tick_label=tick_label, width=0.8, color=['red', 'green'])
    plt.show()


