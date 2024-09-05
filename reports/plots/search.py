from bokeh.embed import components
from bokeh.plotting import figure


FIRE_PALETTE = ['#de0c1c', '#fe2d2d', '#fb7830', '#fecf02']  #, '#ffeea3']


def get_language_plot(data, bar_color='#000'):
    """
    data = {'posemo': 2.060499780797895, 'negemo': 0.7452871547566856, 'anx': 0.131521262604121,
                'anger': 0.08768084173608066, 'sad': 0.5260850504164841, 'social': 3.9017974572555874,
                'cogproc': 9.294169224024545, 'bio': 0.7891275756247259, 'body': 0.08768084173608066},
    """
    original_categories = ['posemo', 'negemo', 'anx', 'anger', 'sad']  #, 'social', 'cogproc', 'bio', 'body']
    new_names = {
        'posemo': 'Positive Emotionen',
        'negemo': 'Negative Emotionen',
        'anx': 'Angst',
        'anger': 'Wut',
        'sad': 'Traurigkeit',
        'social': 'Sozial (?)',
        'cogproc': 'Kognitive Prozesse (?)',
        'bio': 'Physisch (?)',
        'body': 'Körper (?)'
    }

    categories = [new_names[c] for c in original_categories]
    values = [data[c] for c in original_categories]

    p = figure(x_range=categories, height=400, width=400,
               toolbar_location=None, tools="")
    p.vbar(x=categories, top=values, width=0.9,
           fill_color=bar_color, line_color=bar_color)

    p.border_fill_color = None
    p.y_range.start = 0
    p.x_range.range_padding = 0.1
    p.xaxis.major_label_orientation = 1
    p.axis.minor_tick_line_color = None
    p.xgrid.grid_line_color = None
    p.ygrid.grid_line_color = None

    p.xaxis.group_text_color = '#000'
    p.xaxis.group_text_font_size = '10pt'

    p.xaxis.axis_label = 'Emotionalität Ihrer Suchanfragen'
    p.yaxis.axis_label = f'Score'
    p.xaxis.axis_label_text_font_size = '11pt'
    p.yaxis.axis_label_text_font_size = '9pt'
    p.xaxis.axis_label_text_font_style = 'normal'
    p.yaxis.axis_label_text_font_style = 'normal'
    p.xaxis.major_label_text_font_size = '10pt'
    p.xaxis.major_tick_line_color = None

    script, div = components(p)
    return {'script': script, 'div': div}
