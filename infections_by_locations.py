import pandas as pd
import plotly.express as px
import datetime as dt

def location_timeline():
    df = pd.read_csv('covid_out_infections_0.csv')

    start_date = dt.datetime.strptime('2020 September 1', '%Y %B %d').date()
    df['date'] = [start_date + dt.timedelta(days=x) for x in df['#time']]

    df = df[['date', 'location_type']]
    df['number'] = 0

    tab = df.groupby(['date', 'location_type'])['number'].count()
    tab = pd.DataFrame(tab.to_frame()).reset_index()

    dd = pd.DataFrame()
    end_date = max(df['date'])
    num_days = (end_date - start_date).days
    dd['date'] = [start_date + dt.timedelta(days=x) for x in range(num_days+1)]
    tt = list(set(tab['location_type']))
    tt.sort()
    for t in tt:
        dd[t] = 0

    for i in range(len(dd)):
        curr_date = dd.iloc[i]['date']

        temp = tab[tab['date']==curr_date]

        for t in tt:
            data = list(temp[temp['location_type']==t]['number'])
            if len(data) > 0:
                dd[t].iloc[i] = data[0]

    dd = dd.set_index('date')
    fig = px.line(dd)
    fig.show()

def map_plotter(date='2020 September 30'):

    start_date = dt.datetime.strptime('2020 September 1', '%Y %B %d').date()

    rd = dt.datetime.strptime(date, '%Y %B %d').date()

    df = pd.read_csv('covid_out_infections_0.csv')
    df['date'] = [start_date + dt.timedelta(days=x) for x in df['#time']]
    mp = df[df['date'] == rd]

    fig = px.scatter_mapbox(df, lat='y', lon='x', color='location_type', zoom=10.3)
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig.show()

if __name__ == '__main__':
    location_timeline()
    map_plotter()