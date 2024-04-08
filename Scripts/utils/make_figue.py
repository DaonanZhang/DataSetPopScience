import matplotlib.pyplot as plt


labels = ['German', 'Japanese', 'Chinese', 'English']
sizes = [503,1655, 2325, 13615]
colors = ['gold', 'yellowgreen', 'lightcoral', 'lightskyblue']

def autopct_format(values):
    def my_format(pct):
        total = sum(values)
        val = int(round(pct*total/100.0))
        return '{p:.2f}%  ({v:d})'.format(p=pct,v=val)
    return my_format

plt.pie(sizes, labels=labels, colors=colors, autopct=autopct_format(sizes), startangle=140)

plt.axis('equal')

# 显示图形
plt.show()