import pygmt
from eara2022 import resource

eps_path = resource(
    ['paraview', 'model.png'], normal_path=True)


fig = pygmt.Figure()
fig.basemap(region=[105, 162, 0, 59], projection="X4.6i/4.8id", frame=True)

# place
fig.image(
    imagefile=eps_path,
    position="+w4.6i/4.8i",
    box=False,
)

style = "v0.1i+s+e+a40+gorange+h0+p1p,orange"
fig.plot(x=[126], y=[41], style=style,
         pen="0.04i,orange", direction=[[120], [42]])
fig.text(x=120, y=42, text="Gap?",
         font="12p,Helvetica-Bold,black", justify="BR")

fig.show()
