import pygmt

from eara2022 import resource, save_path

eps_path = resource(
    ['paraview', 'model.png'], normal_path=True)


def main():
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
             font="12p,Helvetica-Bold,orange", justify="BR")

    # * texts from the old script
    text_labels = [
        (150, 53, "Sea of Okhotsk", 60),
        (134, 40, "Japan Sea", 30),
        (157, 38, "Pacific Plate", 60),
        (134, 15, "Philippine Sea Plate", 60),
        (115, 15, "South China Sea", 60),
        (114, 27, "South China Block", 0),
        (117, 36.5, "North China", -30),
        (117, 34.5, "Block", -30),
        (120, 48, r"Xing'an-East Mongolia", 30),
    ]

    for x, y, text, angle in text_labels:
        fig.text(x=x, y=y, text=text, font="12p,Helvetica,black", angle=angle)

    # * save
    save_path(fig, "paraview")


if __name__ == "__main__":
    main()
