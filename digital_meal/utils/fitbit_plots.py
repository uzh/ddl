import math

import pandas as pd
from bokeh.embed import components
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
    dfs = []
    relevant_cols = []
    if light_activity is not None:
        light_activity['value'] = light_activity['value'].astype('Int64')
        light_activity.rename(columns={'value': 'leicht'}, inplace=True)
        relevant_cols.append('leicht')
        dfs.append(light_activity)
    if moderate_activity is not None:
        moderate_activity['value'] = moderate_activity['value'].astype('Int64')
        moderate_activity.rename(columns={'value': 'moderat'}, inplace=True)
        relevant_cols.append('moderat')
        dfs.append(moderate_activity)
    if high_activity is not None:
        high_activity['value'] = high_activity['value'].astype('Int64')
        high_activity.rename(columns={'value': 'hoch'}, inplace=True)
        relevant_cols.append('hoch')
        dfs.append(high_activity)

    if len(dfs) == 0:
        return None

    activity = dfs[0].set_index('dateTime')
    for df in range(1, len(dfs)):
        activity = activity.join(dfs[df].set_index('dateTime'))

    activity.reset_index(inplace=True)
    activity['dateTime'] = pd.to_datetime(activity['dateTime'])
    activity = activity.replace('', None)

    max_y = activity[relevant_cols].sum(axis=1).max()
    stack_colors = ('#004488', '#DDAA33', '#BB5566')[:len(relevant_cols)]

    p = figure(
        x_axis_type='datetime',
        y_range=(0, max_y + 20),
        toolbar_location=None,
    )
    p.varea_stack(
        stackers=relevant_cols,
        x='dateTime',
        color=stack_colors,
        legend_label=relevant_cols,
        source=activity
    )

    p.legend.orientation = 'horizontal'
    p.legend.background_fill_color = 'white'
    p.background_fill_color = '#F1EDFF'
    p.border_fill_color = None
    p.grid.grid_line_color = None
    p.grid.minor_grid_line_color = '#eeeeee'
    p.axis.minor_tick_line_color = None
    p.xaxis.major_label_orientation = math.pi/3

    script, div = components(p)

    activity_date_min = pd.to_datetime(activity.dateTime.min())
    activity_date_max = pd.to_datetime(activity.dateTime.max())
    return {'script': script, 'div': div}, activity_date_min, activity_date_max
