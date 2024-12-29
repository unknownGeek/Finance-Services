import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from Constants import featureFlagToPlotRelevantPrices

plt.ion()

plt.rcParams["figure.figsize"] = [6, 9.6]

class DynamicUpdate():

    def on_launch(self, index):
        #Set up plot
        self.figure1, (self.ax1, self.ax2, self.ax3, self.ax4) = plt.subplots(nrows=4, ncols=1, constrained_layout=True)
        self.lines1, = self.ax1.plot([], [], '-b', label='PCR from-total-chng-OI')
        self.lines2, = self.ax1.plot([], [], '-y', label='PCR from-total-OI')
        self.ax1.set_ylabel('PCR')
        self.lines3, = self.ax2.plot([], [], '-r', label='CALLs[Bears/DOWN]')
        self.lines4, = self.ax2.plot([], [], '-g', label='PUTs[Bulls/UP]')
        self.ax2.set_ylabel('Total OI[Open Interest]')
        self.lines5, = self.ax3.plot([], [], '-r', label='CALLs[Bears/DOWN]')
        self.lines6, = self.ax3.plot([], [], '-g', label='PUTs[Bulls/UP]')
        self.ax3.set_ylabel('Total Change in OI')
        self.lines7, = self.ax4.plot([], [], '-b', label='underlyingValue')
        self.ax4.set_ylabel('Market Price')

        if featureFlagToPlotRelevantPrices:
            self.lines8, = self.ax1.plot([], [], '--g', label='RELEVANT PCR from-total-chng-OI')
            self.lines9, = self.ax2.plot([], [], '--b', label='RELEVANT CALLs[Bears/DOWN]')
            self.lines10, = self.ax2.plot([], [], '--y', label='RELEVANT PUTs[Bulls/UP]')
            self.lines11, = self.ax3.plot([], [], '--b', label='RELEVANT CALLs[Bears/DOWN]')
            self.lines12, = self.ax3.plot([], [], '--y', label='RELEVANT PUTs[Bulls/UP]')

        self.figure1.suptitle(f'Charts for index={index}', fontsize=16)
        self.ax1.legend()
        self.ax2.legend()
        self.ax3.legend()
        self.ax4.legend()
        plt.xlabel('Time')
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        plt.gcf().autofmt_xdate()


    def on_running(self, xdata, y1data, y2data, y3data, y4data, y5data, y6data, y7data, y8data, y9data, y10data, y11data, y12data):
        #Update data (with the new _and_ the old points)
        self.lines1.set_xdata(xdata)
        self.lines1.set_ydata(y1data)
        self.lines2.set_xdata(xdata)
        self.lines2.set_ydata(y2data)
        self.lines3.set_xdata(xdata)
        self.lines3.set_ydata(y3data)
        self.lines4.set_xdata(xdata)
        self.lines4.set_ydata(y4data)
        self.lines5.set_xdata(xdata)
        self.lines5.set_ydata(y5data)
        self.lines6.set_xdata(xdata)
        self.lines6.set_ydata(y6data)
        self.lines7.set_xdata(xdata)
        self.lines7.set_ydata(y7data)

        if featureFlagToPlotRelevantPrices:
            self.lines8.set_xdata(xdata)
            self.lines8.set_ydata(y8data)
            self.lines9.set_xdata(xdata)
            self.lines9.set_ydata(y9data)
            self.lines10.set_xdata(xdata)
            self.lines10.set_ydata(y10data)
            self.lines11.set_xdata(xdata)
            self.lines11.set_ydata(y11data)
            self.lines12.set_xdata(xdata)
            self.lines12.set_ydata(y12data)

        #Need both of these in order to rescale
        self.ax1.relim()
        self.ax1.autoscale_view()
        self.ax2.relim()
        self.ax2.autoscale_view()
        self.ax3.relim()
        self.ax3.autoscale_view()
        self.ax4.relim()
        self.ax4.autoscale_view()
        #We need to draw *and* flush
        self.figure1.canvas.draw()
        self.figure1.canvas.flush_events()


# STRONG BEARISH Market =>
# Case:1 :
#       If 'PCR from-total-chng-OI' goes down from 2 towards 1 consistently,
#   and If 'Total OI' [Green line above Red line] remains constant or tends to cross-over




