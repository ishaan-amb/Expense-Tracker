# import packages required
import matplotlib.pyplot as plt

from db import *

def plotByDatePie():
    sum_by_date = sum_by_day()
    labels = []
    sizes = []
    colors = ['gold', 'yellowgreen', 'lightcoral', 'lightskyblue']
    explode = (0.1, 0, 0, 0)  # explode 1st slice
    i = 0
    for record in sum_by_date:
        i+= 1
        print('For date:', record['_id'], 'the total expense is:', record['total'])
        labels.append(record["_id"][6:]+"/"+record["_id"][:4:7]+"/"+record['_id'][:4:])
        sizes.append(record["total"])

    plt.pie(sizes, labels=labels, colors=colors,
    autopct='%1.1f%%', shadow=True, startangle=140)
    plt.axis('equal')
    plt.show()

def plotByCategoryPie():
    sum_by_cat = sum_by_category()
    labels = []
    sizes = []
    colors = ['gold', 'yellowgreen', 'lightcoral', 'lightskyblue']
    explode = (0.1, 0, 0, 0)  # explode 1st slice
    i=0
    for record in sum_by_cat:
        i+=1
        labels.append(record['_id'])
        sizes.append(record['total'])

    plt.pie(sizes, labels=labels, colors=colors,
    autopct='%1.1f%%', shadow=True, startangle=140)
    plt.axis('equal')
    plt.show()

