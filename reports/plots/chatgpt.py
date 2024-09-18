from bokeh.embed import components
from bokeh.models import Span
from bokeh.plotting import figure

INSTA_CATEGORIES = ['Parteien', 'Politiker:innen', 'Medien', 'Organisationen']
FIRE_PALETTE = ['#b0020f', '#fe2d2d', '#fb7830', '#fecf02']  #, '#ffeea3']

TRUST_SCALE = [
    'vertraue ich\nvoll und ganz',
    'vertraue ich eher',
    'unentschieden',
    'vertraue ich\neher nicht',
    'vertraue ich\nnicht'
]
TRUST_VALUES = [1, 2, 3, 4, 5]

AGREEMENT_SCALE = [
    'stimme voll und\nganz zu',
    'stimme eher zu',
    'unentschieden',
    'stimme eher\nnicht zu',
    'stimme nicht zu'
]
AGREEMENT_VALUES = [1, 2, 3, 4, 5]

PLOT_CONFIG = {
    'trust-chatgpt': {
        'categories': TRUST_SCALE,
        'survey_values': TRUST_VALUES,
        'ref_values': [3, 12, 34, 26, 18]
    },
    'trust-science': {
        'categories': TRUST_SCALE,
        'survey_values': TRUST_VALUES,
        'ref_values': [11, 48, 36, 4, 1]
    },
    'benefit-chatgpt-1': {
        'categories': AGREEMENT_SCALE,
        'survey_values': AGREEMENT_VALUES,
        'ref_values': [22, 28, 23, 10, 11]
    },
    'benefit-chatgpt-2': {
        'categories': AGREEMENT_SCALE,
        'survey_values': AGREEMENT_VALUES,
        'ref_values': [13, 19, 20, 17, 25]
    },
    'benefit-chatgpt-3': {
        'categories': AGREEMENT_SCALE,
        'survey_values': AGREEMENT_VALUES,
        'ref_values': [20, 28, 27, 8, 12]
    },
    'risk-chatgpt-1': {
        'categories': AGREEMENT_SCALE,
        'survey_values': AGREEMENT_VALUES,
        'ref_values': [41, 18, 20, 6, 8]
    },
    'risk-chatgpt-2': {
        'categories': AGREEMENT_SCALE,
        'survey_values': AGREEMENT_VALUES,
        'ref_values': [34, 23, 18, 8, 9]
    },
    'risk-chatgpt-3': {
        'categories': AGREEMENT_SCALE,
        'survey_values': AGREEMENT_VALUES,
        'ref_values': [40, 21, 19, 7, 7]
    },
    'gender': '2',
    'age': '2',
}


def get_bar_plot(var_name, response):
    categories = PLOT_CONFIG[var_name]['categories']
    counts = PLOT_CONFIG[var_name]['ref_values']

    p = figure(x_range=categories, height=350,
               toolbar_location=None, tools="",
               y_axis_label="Anteil der Befragten (in %)")

    p.vbar(x=categories, top=counts, width=0.9)

    try:
        resp = int(response)
        if resp in PLOT_CONFIG[var_name]['survey_values']:
            p.add_layout(Span(location=resp-0.5, dimension='height', line_width=6, line_color='orange', level='overlay'))
    except ValueError:
        pass

    p.xgrid.grid_line_color = None
    p.y_range.start = 0

    p.axis.minor_tick_line_color = None

    script, div = components(p)
    return {'script': script, 'div': div}
