import math

import pandas as pd
from bokeh.embed import components
from bokeh.models.ranges import FactorRange
from bokeh.palettes import tol
from bokeh.plotting import figure


def get_sleep_plot(data):
    data['timestamp'] = pd.to_datetime(data['timestamp'])
    data = data.replace('', None)
    data['deep_sleep_in_minutes'] = data['deep_sleep_in_minutes'].astype('Int64')
    data['resting_heart_rate'] = data['resting_heart_rate'].astype('Int64')
    data['duration_score'] = data['duration_score'].astype('Int64')

    p = figure(
        x_axis_type='datetime',
        y_range=(0, data['deep_sleep_in_minutes'].max() + 20),
        toolbar_location=None,
        height=300
    )
    p.line(x='timestamp', y='deep_sleep_in_minutes', line_width=3, source=data)
    p.border_fill_color = None
    p.grid.grid_line_color = None
    p.axis.minor_tick_line_color = None
    p.background_fill_color = '#fff2ba'
    script, div = components(p)
    return {'script': script, 'div': div}


def get_heart_rate_sleep_plot(data):
    data['timestamp'] = pd.to_datetime(data['timestamp'])
    data = data.replace('', None)
    data['deep_sleep_in_minutes'] = data['deep_sleep_in_minutes'].astype('Int64')
    data['resting_heart_rate'] = data['resting_heart_rate'].astype('Int64')
    data['duration_score'] = data['duration_score'].astype('Int64')

    p = figure(
        x_axis_type='datetime',
        y_range=(0, data['resting_heart_rate'].max() + 20),
        toolbar_location=None,
        height=300
    )
    p.line(x='timestamp', y='resting_heart_rate', line_width=3, color='orange', source=data)
    p.border_fill_color = None
    p.grid.grid_line_color = None
    p.axis.minor_tick_line_color = None
    p.background_fill_color = '#fff2ba'
    script, div = components(p)
    return {'script': script, 'div': div}


def get_steps_plot(data):
    data['dateTime'] = pd.to_datetime(data['dateTime'])
    data = data.replace('', None)
    data['value'] = data['value'].astype('Int64')
    data_days = data.set_index('dateTime').groupby(pd.Grouper(freq='1D')).sum()

    p = figure(
        x_axis_type='datetime',
        y_range=(0, data_days['value'].max() + 200),
        toolbar_location=None,
        height=300
    )
    p.line(x='dateTime', y='value', line_width=3, color='purple', source=data_days)
    p.border_fill_color = None
    p.grid.grid_line_color = None
    p.axis.minor_tick_line_color = None
    p.background_fill_color = '#bbf3d4'
    script, div = components(p)
    return {'script': script, 'div': div}


def get_active_minutes_plot(light_activity, moderate_activity, high_activity):
    # rename dataframes
    if light_activity is not None:
        light_activity.rename(columns={'value': 'leicht'}, inplace=True)
    if moderate_activity is not None:
        moderate_activity.rename(columns={'value': 'moderat'}, inplace=True)
    if high_activity is not None:
        high_activity.rename(columns={'value': 'hoch'}, inplace=True)

    activity = light_activity.set_index('dateTime').join(moderate_activity.set_index('dateTime'))
    activity = activity.join(high_activity.set_index('dateTime'))

    activity.reset_index(inplace=True)
    activity['dateTime'] = pd.to_datetime(activity['dateTime'])
    activity = activity.replace('', None)

    activity['leicht'] = activity['leicht'].astype(int)
    activity['moderat'] = activity['moderat'].astype(int)
    activity['hoch'] = activity['hoch'].astype(int)

    max_y = activity[['leicht', 'moderat', 'hoch']].sum(axis=1).max()

    p = figure(
        x_axis_type='datetime',
        y_range=(0, max_y + 20),
        toolbar_location=None,
    )
    p.grid.minor_grid_line_color = '#eeeeee'

    names = ['leicht', 'moderat', 'hoch']
    p.varea_stack(stackers=names, x='dateTime', color=tol['HighContrast'][3], legend_label=names, source=activity)

    p.legend.orientation = 'horizontal'
    p.legend.background_fill_color = 'white'
    p.background_fill_color = '#F1EDFF'  # #D0C3FF
    p.border_fill_color = None
    p.grid.grid_line_color = None
    p.axis.minor_tick_line_color = None
    p.xaxis.major_label_orientation = math.pi/3

    script, div = components(p)
    return {'script': script, 'div': div}
