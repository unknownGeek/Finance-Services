import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go

x = np.linspace(0, 10, 1000)
y= 3*x**2 - 2*x**2 + 4*x- 5

data = dict(type='scatter', x=x, y=y, mode='markers')
figure = go.Figure(data=data)

figure.layout.title = 'Testing'
figure.layout.xaxis.title = 'x'
figure.layout.yaxis.title = 'y'
f2 = go.FigureWidget(figure)
figure.data[0].x=[2]
figure.data[0].y=[4]
f2 = go.FigureWidget(figure)
f2.show()



# fig = px.line(x=x ,y =y,labels={'x':'x', 'y':'y'})
#
# df = px.data.stocks()
# fig = px.line(df, x='date', y=["MSFT","GOOG",'FB',"AMZN"])
# fig.show()
#
# figure = go.Figure(data=data, layout=layout)
#
# f2 = go.FigureWidget(figure)
# f2
