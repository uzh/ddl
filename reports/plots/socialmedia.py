from bokeh.embed import components
from bokeh.models import Legend, Span, FactorRange, ColumnDataSource
from bokeh.plotting import figure
from bokeh.transform import factor_cmap
from django.conf import settings
from statistics import mean
from ..models import InstagramStatistics

INSTA_CATEGORIES = ['Parteien', 'Politiker:innen', 'Medien', 'Organisationen']
FIRE_PALETTE = ['#b0020f', '#fe2d2d', '#fb7830', '#fecf02']  #, '#ffeea3']


def load_instagram_statistics():
    try:
        stats = InstagramStatistics.objects.get(pk=1)
    except InstagramStatistics.DoesNotExist:
        stats = InstagramStatistics(name='Instastats', project_pk=settings.INSTAGRAM_PROJECT_PK)
        stats.save()

    if not stats.last_updated:
        try:
            stats.update_statistics()
        except:
            pass
    return stats


def get_custom_legend(p):
    label_colors = {
        'Parteien': FIRE_PALETTE[0],
        'Politiker:innen': FIRE_PALETTE[1],
        'Medien': FIRE_PALETTE[2],
        'Organisationen': FIRE_PALETTE[3]
    }
    legend_items = [(label, [p.square(-10, -10, legend_label=label, color=label_colors[label])]) for label in
                    INSTA_CATEGORIES]
    legend = Legend(items=legend_items, location='center',
                    background_fill_color=None, border_line_color=None,
                    orientation='horizontal')
    return legend


def get_follows_plot(followed_accounts):
    n_total = sum([len(followed_accounts[key]) for key in followed_accounts.keys()])
    n_relevant = n_total - len(followed_accounts['other'])

    dimension = ['Gefolgte Accounts']
    categories = INSTA_CATEGORIES
    palette = FIRE_PALETTE

    data = {
        'Gefolgte Accounts': dimension,
        'Parteien': [len(followed_accounts['party'])],
        'Politiker:innen': [len(followed_accounts['politician'])],
        'Medien': [len(followed_accounts['media'])],
        'Organisationen': [len(followed_accounts['organisation'])],
        # 'andere (nicht politisch)': [len(followed_accounts['other'])],
    }

    p = figure(y_range=dimension, x_range=(0, n_relevant), height=140, width=800, toolbar_location=None,
               tools='hover', tooltips='$name: @$name',
               background_fill_color=None)

    p.hbar_stack(categories, y='Gefolgte Accounts', height=0.9, color=palette, source=ColumnDataSource(data),
                 legend_label=categories)

    p.border_fill_color = None
    p.y_range.range_padding = 0.1
    p.yaxis.visible = False
    p.ygrid.visible = False
    p.xgrid.visible = False
    p.axis.minor_tick_line_color = None
    p.outline_line_color = None

    p.legend.visible = False
    legend = get_custom_legend(p)
    p.add_layout(legend, 'below')

    script, div = components(p)
    return {'script': script, 'div': div}


def get_line_plot(followed_accounts):
    def draw_line(plot, y, x_a, x_b, color):
        plot.add_layout(Span(location=y, dimension='width', line_width=2, line_color='lightgray', level='underlay'))
        plot.square(x=x_a, y=y, size=15, color=color)
        plot.triangle(x=x_b, y=y, size=15, color=color)

    def get_max(followed_accounts, ref_accounts):
        max_n = [40]
        categories = ['party', 'politician', 'media', 'organisation']
        if ref_accounts:
            for c in categories:
                max_n.append(max(ref_accounts[c]))

        if followed_accounts:
            for c in categories:
                max_n.append(len(followed_accounts[c]))

        return max(max_n) + 10

    reference_stats = load_instagram_statistics()
    ref_accounts = reference_stats.follow_counts

    x_max = get_max(followed_accounts, ref_accounts)
    p = figure(
        tools="",
        toolbar_location=None,
        background_fill_color='#fff',
        x_range=(0, x_max),
        height=300, width=800,
    )
    p.grid.grid_line_color = None

    if ref_accounts:
        # x_a = person, x_b = reference group
        draw_line(p, 4, len(followed_accounts['party']), mean(ref_accounts['party']), '#de0c1c')
        draw_line(p, 3, len(followed_accounts['politician']),  mean(ref_accounts['politician']), '#fe2d2d')
        draw_line(p, 2, len(followed_accounts['media']),  mean(ref_accounts['media']), '#fb7830')
        draw_line(p, 1, len(followed_accounts['organisation']),  mean(ref_accounts['organisation']), '#fecf02')
    else:
        draw_line(p, 4, len(followed_accounts['party']), -10, '#de0c1c')
        draw_line(p, 3, len(followed_accounts['politician']),  -10, '#fe2d2d')
        draw_line(p, 2, len(followed_accounts['media']),  -10, '#fb7830')
        draw_line(p, 1, len(followed_accounts['organisation']), -10, '#fecf02')

    # Customize plot appearance
    p.yaxis.major_label_overrides = {4: 'Parteien', 3.5: '', 3: 'Politiker', 2.5: '', 2: 'Medien', 1.5: '',
                                     1: 'Organisationen'}

    p.axis.minor_tick_line_color = None
    p.axis.major_tick_line_color = None
    p.outline_line_color = None

    p.yaxis.major_label_text_font_size = '12pt'

    p.xaxis.axis_line_color = None
    p.xaxis.axis_label = 'Anzahl gefolgte Accounts'

    # Add custom legend
    legend_items = [
        ('Sie', [p.square(x=-5, y=2, size=15, color='#000', legend_label='Sie')]),
        ('Durchschnitt', [p.triangle(x=-5, y=2, size=15, color='#000', legend_label='Durchschnitt')])
    ]
    p.legend.visible = False
    legend = Legend(items=legend_items, location='right',
                    background_fill_color=None, border_line_color=None,
                    orientation='horizontal')
    p.add_layout(legend, 'above')

    script, div = components(p)
    return {'script': script, 'div': div}


def get_interaction_plot(interactions):
    def get_list_for_plot(category, interactions):
        l = []
        for interaction in ['likes_posts', 'likes_stories', 'comments_general', 'comments_reels']:
            l.append(len(interactions[interaction][category]))
        return l

    interaction_types = [
        'Likes\nPosts',  # 'likes_posts',
        'Likes\nStories',  # 'likes_stories',
        'Kommentare\nallgemein',  # 'comments_general',
        'Kommentare\nReels'  # 'comments_reels'
    ]
    categories = INSTA_CATEGORIES
    data = {
        'interactions': interaction_types,
        'Parteien': get_list_for_plot('party', interactions),
        'Politiker:innen': get_list_for_plot('politician', interactions),
        'Medien': get_list_for_plot('media', interactions),
        'Organisationen': get_list_for_plot('organisation', interactions),
        # 'andere (nicht politisch)': get_list_for_plot('other', interactions),
    }

    palette = FIRE_PALETTE
    x = [(interaction, category) for interaction in interaction_types for category in categories]
    counts = sum(zip(data['Parteien'], data['Politiker:innen'], data['Medien'], data['Organisationen']), ())
    source = ColumnDataSource(data=dict(x=x, counts=counts))

    p = figure(x_range=FactorRange(*x), height=350, width=800,
               toolbar_location=None, tools="", background_fill_color=None)

    p.vbar(x='x', top='counts', width=0.9, source=source, line_color='white',
           fill_color=factor_cmap('x', palette=palette, factors=categories, start=1, end=2))

    p.border_fill_color = None
    p.y_range.start = 0
    p.x_range.range_padding = 0.1
    p.axis.minor_tick_line_color = None

    p.xaxis.major_label_orientation = 1
    p.xaxis.major_label_text_font_size = '1pt'
    p.xaxis.major_label_text_alpha = 0
    p.xaxis.group_text_color = '#000'
    p.xaxis.group_text_font_size = '10pt'

    p.xgrid.grid_line_color = None

    legend = get_custom_legend(p)
    p.legend.visible = False
    p.add_layout(legend, 'below')

    script, div = components(p)
    return {'script': script, 'div': div}


def get_content_plot(content):
    def get_list_for_plot(category, interactions):
        l = []
        for interaction in ['seen_ads', 'recommended_profiles', 'seen_posts', 'seen_videos']:
            l.append(len(interactions[interaction][category]))
        return l

    interaction_types = [
        'Geschaute\nWerbung',
        'Vorgeschlagene\nProfile',
        'Geschaute\nPosts',
        'Geschaute\nVideos'
    ]
    categories = INSTA_CATEGORIES
    data = {
        'interactions': interaction_types,
        'Parteien': get_list_for_plot('party', content),
        'Politiker:innen': get_list_for_plot('politician', content),
        'Medien': get_list_for_plot('media', content),
        'Organisationen': get_list_for_plot('organisation', content),
        # 'andere (nicht politisch)': get_list_for_plot('other', content),
    }

    palette = FIRE_PALETTE

    x = [(interaction, category) for interaction in interaction_types for category in categories]
    counts = sum(zip(data['Parteien'], data['Politiker:innen'], data['Medien'], data['Organisationen']), ())

    source = ColumnDataSource(data=dict(x=x, counts=counts))

    p = figure(x_range=FactorRange(*x), height=350, width=800,
               toolbar_location=None, tools="", background_fill_color=None)

    p.vbar(x='x', top='counts', width=1, source=source, line_color='white',
           fill_color=factor_cmap('x', palette=palette, factors=categories, start=1, end=2))

    p.border_fill_color = None
    p.y_range.start = 0
    p.x_range.range_padding = 0.1

    p.axis.minor_tick_line_color = None

    p.xaxis.major_label_orientation = 1
    p.xaxis.major_label_text_font_size = '1pt'
    p.xaxis.major_label_text_alpha = 0
    p.xaxis.group_text_color = '#000'
    p.xaxis.group_text_font_size = '10pt'

    p.xgrid.grid_line_color = None

    legend = get_custom_legend(p)
    p.legend.visible = False
    p.add_layout(legend, 'below')

    script, div = components(p)
    return {'script': script, 'div': div}


def get_vote_graph(data, color='1'):
    colors = {
        '1': '#fbe122',
        '2': '#002b79'
    }
    categories = ['ja', 'nein', 'leer', 'nicht teilgenommen']
    labels = ['ja', 'nein', 'leer', 'nicht\nteilgenommen']
    counts = [data[cat] for cat in categories]
    p = figure(x_range=labels, height=250, width=500,
               toolbar_location=None, tools="")
    p.vbar(x=labels, top=counts, width=0.9,
           fill_color=colors[color], line_color='white')

    p.border_fill_color = None
    p.y_range.start = 0
    p.x_range.range_padding = 0.1
    p.axis.minor_tick_line_color = None
    p.xgrid.grid_line_color = None

    p.xaxis.group_text_color = '#000'
    p.xaxis.group_text_font_size = '10pt'

    p.xaxis.axis_label = 'Abstimmungsverhalten'
    p.yaxis.axis_label = 'Anzahl Personen'
    p.xaxis.axis_label_text_font_size = '11pt'
    p.yaxis.axis_label_text_font_size = '11pt'
    p.xaxis.axis_label_text_font_style = 'normal'
    p.yaxis.axis_label_text_font_style = 'normal'
    p.xaxis.major_label_text_font_size = '10pt'
    p.xaxis.major_tick_line_color = None

    script, div = components(p)
    return {'script': script, 'div': div}


def get_party_graph(data, key):
    colors = {
        'SP': '#e4002b',
        'SVP': '#009f4e',
        'Mitte': '#ff9b00',
        'FDP': '#074ea1'
    }

    reference_stats = load_instagram_statistics()
    data = reference_stats.party_counts

    categories = [str(i) for i in range(1, 11)]
    counts = [data[key][cat] for cat in categories]

    p = figure(x_range=categories, height=400, width=400,
               toolbar_location=None, tools="")
    p.vbar(x=categories, top=counts, width=0.9,
           fill_color='white', line_color='white')

    p.background_fill_color = colors[key]
    p.border_fill_color = None
    p.y_range.start = 0
    p.x_range.range_padding = 0.1
    p.axis.minor_tick_line_color = None
    p.xgrid.grid_line_color = None
    p.ygrid.grid_line_color = None

    p.xaxis.group_text_color = '#000'
    p.xaxis.group_text_font_size = '10pt'

    p.xaxis.axis_label = 'Politische Ausrichtung\n(von 1=links bis 10=rechts)'
    p.yaxis.axis_label = f'Anzahl Personen, die einem {key}-Account folgen'
    p.xaxis.axis_label_text_font_size = '11pt'
    p.yaxis.axis_label_text_font_size = '9pt'
    p.xaxis.axis_label_text_font_style = 'normal'
    p.yaxis.axis_label_text_font_style = 'normal'
    p.xaxis.major_label_text_font_size = '10pt'
    p.xaxis.major_tick_line_color = None

    script, div = components(p)
    return {'script': script, 'div': div}
