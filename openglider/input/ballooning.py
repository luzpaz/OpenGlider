from openglider.glider.ballooning import BallooningBezier
from openglider.input import ControlPoint, MplWidget, ApplicationWindow, MplBezier


def input_ballooning(ballooning):
    assert isinstance(ballooning, BallooningBezier)
    upper = ballooning.upbez
    lower = ballooning.lowbez
    cp_upper = [ControlPoint([p[0], 10*p[1]]) for p in upper.controlpoints]
    cp_lower = [ControlPoint([p[0], -10*p[1]]) for p in lower.controlpoints]
    mpl = MplWidget(dpi=100)
    aw = ApplicationWindow([mpl])

    upper_curve = MplBezier(cp_upper)
    lower_curve = MplBezier(cp_lower)
    upper_curve.insert_mpl(mpl)
    lower_curve.insert_mpl(mpl)

    def set_points(x):
        ballooning.controlpoints = [[[p.point[0], p.point[1]*0.1] for p in upper_curve.controlpoints],
                                    [[p.point[0], -p.point[1]*0.1] for p in lower_curve.controlpoints]]
        print("updated")

    aw.buttons[0].clicked.connect(set_points)
    return aw