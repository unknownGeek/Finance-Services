import matplotlib.pyplot as plt
import numpy as np

x = np.arange(5)
y = np.exp(x)
fig1, ax1 = plt.subplots()
ax1.plot(x, y)
ax1.set_title("Axis 1 title")
ax1.set_xlabel("X-label for axis 1")

z = np.sin(x)
fig2, (ax2, ax3) = plt.subplots(nrows=2, ncols=1) # two axes on figure
ax2.plot(x, z)
ax3.plot(x, -z)

w = np.cos(x)
ax1.plot(x, w) # can continue plotting on the first axis
ax1.plot(x, np.cos(np.sin(x))) # can continue plotting on the first axis

plt.show()







import matplotlib.pyplot as plt

plt.ion()

class DynamicUpdate():

    def on_launch(self, index):
        #Set up plot
        self.figure1, self.ax1 = plt.subplots()
        self.lines1, = self.ax1.plot([], [], '-b', label=index+'- PCR[from-total-chng-OI]')
        self.lines2, = self.ax1.plot([], [], '-y', label=index+'- PCR[from-total-OI]')
        self.figure2, self.ax2 = plt.subplots()
        self.lines3, = self.ax2.plot([], [], '-g', label=index+'- totalCallOI')
        self.lines4, = self.ax2.plot([], [], '-r', label=index+'- totalPutOI')
        self.ax1.legend()
        self.ax2.legend()


    def on_running(self, xdata, y1data, y2data, y3data, y4data):
        #Update data (with the new _and_ the old points)
        self.lines1.set_xdata(xdata)
        self.lines1.set_ydata(y1data)
        self.lines2.set_xdata(xdata)
        self.lines2.set_ydata(y2data)
        self.lines3.set_xdata(xdata)
        self.lines3.set_ydata(y3data)
        self.lines4.set_xdata(xdata)
        self.lines4.set_ydata(y4data)
        #Need both of these in order to rescale
        self.ax1.relim()
        self.ax1.autoscale_view()
        self.ax2.relim()
        self.ax2.autoscale_view()
        #We need to draw *and* flush
        self.figure1.canvas.draw()
        self.figure1.canvas.flush_events()
        self.figure2.canvas.draw()
        self.figure2.canvas.flush_events()

