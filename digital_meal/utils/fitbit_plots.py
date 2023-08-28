from bokeh.embed import components


def get_sleep_plot(data):
    p = None
    script, div = components(p)
    return {'script': script, 'div': div}


def get_steps_plot(data):
    p = None
    script, div = components(p)
    return {'script': script, 'div': div}


def get_active_minutes_plot(data):
    p = None
    script, div = components(p)
    return {'script': script, 'div': div}
