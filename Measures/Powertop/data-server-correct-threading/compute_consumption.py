import numpy as np
import matplotlib.pyplot as plt
x = np.array([0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
y = (np.array([51.9, 107, 117, 127, 137, 146, 157, 172, 200, 227, 245])/2)-10
z = np.polyfit(x, y, 5)
f = np.poly1d(z)
x_new = np.linspace(x[0], x[-1], 50)
y_new = f(x_new)
fig, ax = plt.subplots()
ax.plot(x,y,'o', label="discrete values")
ax.plot(x_new,y_new, label="continous values")
plt.xlim([x[0]-1, x[-1] + 1 ])
ax.set_xlabel("Load (%)")
ax.set_ylabel("Consumption (W)")
ax.legend()

i=float(100/28)
while i<=100:
    print(str(round(f(i), 2)) + " W  ")
    i+=float(100/28)

plt.show()
