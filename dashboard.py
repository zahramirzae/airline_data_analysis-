import pandas as pd
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
import plotly.express as px
import plotly.graph_objects as go
from matplotlib.ticker import FixedFormatter
import jdatetime

st.set_page_config(page_title='Snapp Dashboard', page_icon=None, layout="wide")
st.title= 'Snapp Dashboard'

st.markdown(
    """
    <style>
    body {
        background-color: #F8F8F8;  /* Light gray background color */
    }
    </style>
    """,
    unsafe_allow_html=True
)


file_path="/home/zahra.mirzaei/khiar_proj/SnappTrip_BA_Task.csv"
@st.cache_data
def load_data():
    df = pd.read_csv(file_path)
    df = df.fillna(0)
    df['Flightdate'] = pd.to_datetime(df['Flightdate'])
    # df['Flightdate'] = df['Flightdate'].dt.date
    df['persian_time'] = df['Flightdate'].apply(lambda x: jdatetime.datetime. \
                                                fromgregorian(datetime=x).strftime('%Y-%m-%d'))
    df['persian_year'] = df['persian_time'].apply(lambda x: int(x.split('-')[0]))
    df['persian_month'] = df['persian_time'].apply(lambda x: int(x.split('-')[1]))
    df['persian_day'] = df['persian_time'].apply(lambda x: int(x.split('-')[2]))
    #   df['year']=df['Created Date'].dt.year
    #   df['month']=df['Created Date'].dt.month
    df['MarkUp'] = df['MarkUp'].astype(int)
    df['System Type'] = df['System Type'].astype(str)
    df['Origin'] = df['Origin'].astype(str)
    df['Destination'] = df['Destination'].astype(str)
    df['GMV'] = df['GMV'].astype(int)
    df['Commission'] = df['Commission'].mask(df['Commission'] == 0).fillna(df['GMV'] * 0.04)
    df['Commission'] = df['Commission'].astype(int)
    df['Dump'] = df['Dump'].astype(int)
    df['Revenue'] = df['Commission'] + df['MarkUp']
    df['Cost'] = df['Dump']
    df['Profit'] = df['Revenue'] - df['Cost']
    # df['season'] = (df['Created Date'].dt.month % 12 + 3) // 3
    return df

df=load_data()

# st.sidebar.title("Filter data")
#
# # productid_list = st.sidebar.multiselect("Select Product ID", df1['Product ID'].unique())
# # empid_list = st.sidebar.multiselect("Select Employee ID", df3['EMP ID'].unique())
# # supervisor_list = st.sidebar.multiselect("Select Supervisor", df3['Supervisor'].unique())
# start_date=df['Flightdate'].iloc[0]
# end_date=df['Flightdate'].iloc[len(df['Flightdate'])-1]
# start_date = st.sidebar.date_input('Start date', start_date)
# end_date = st.sidebar.date_input('End date', end_date)
# if start_date < end_date:
#     st.sidebar.success('Start date: `%s`\n\nEnd date:`%s`' % (start_date, end_date))
# else:
#     st.sidebar.error('Error: End date must fall after start date.')
#
# st.sidebar.checkbox("Apply Filter")

data_container = st.container()
with data_container:
    st.markdown('Snapp Dashboard')
    kpi1, kpi2, kpi3 = st.columns(3)
    with kpi1:
        kpi1.metric(
            label="Cost",
            value='30B',
            delta='3B',
        )
    with kpi2:
        kpi2.metric(
            label="Revenue",
            value='4000B',
            delta='1900',
        )
    with kpi3:
        kpi3.metric(
            label="Profit",
            value='3500B',
            delta='1900',
        )
# --------------------Ticket sold by date----------------------------
df_flight= df.loc[(df['persian_year']==1401) & (df['Is Cancelled']==False) & (df['persian_month']==12)]
df_flight= df_flight.groupby('persian_time')['Tickets'].sum().reset_index()

fig1 = px.line(df_flight, x="persian_time", y="Tickets", text="Tickets")
fig1.update_traces(textposition="bottom right")
fig1.update_layout(plot_bgcolor="white",title_text='Tickets sold by date-Last 30 days')


#--------------------------demand by city--------------------------------
demand_df = df.loc[(df['persian_year'] == 1401) & (df['persian_month'] >= 6)]
demand=pd.DataFrame(demand_df.groupby(['Origin','System Type'])['Tickets'].sum().reset_index())
demand = demand.sort_values('Tickets', ascending=False)
demand=demand.iloc[:20,:]
fig2 = px.bar(demand, y="Origin", x="Tickets", color="System Type", title="15 Most in demand -By city",orientation='h')
demand_fig=fig2.update_layout(width=500, height=500,plot_bgcolor="white")
fig2.update_xaxes(tickformat="%d-%m-%Y")


#---------------- profit water fall -------------------------------
profit_1400= df.loc[(df['persian_year'] == 1400) & (df['persian_month'] >=6)].\
groupby('persian_month')['Profit'].sum().rename('profit_1400').reset_index()
profit_1401= df.loc[(df['persian_year'] == 1401) & (df['persian_month'] >=6)].\
groupby('persian_month')['Profit'].sum().rename('profit_1401').reset_index()
merged_df = pd.merge(profit_1400, profit_1401, on='persian_month', how='inner')
merged_df['profit'] = (merged_df['profit_1401'] - merged_df['profit_1400'])
categories = merged_df['persian_month']
values = merged_df['profit']

# fig3, ax = plt.subplots()
# # Set the initial position of the bars
# pos = range(len(categories))
# # Create the bars for positive values
# ax.bar(pos, [max(0, value) for value in values], color='green')
# # Create the bars for negative values
# ax.bar(pos, [min(0, value) for value in values], color='red')
# # Set the labels and title
# ax.set_xticks(pos)
# ax.set_xticklabels(categories)
# ax.set_ylabel('Profit Value')
# ax.set_xlabel('Month')
# ax.set_title('Profit Waterfall Plot - Last 6 months')
# # Change y-axis labels to "k" format
# def format_thousands(x, pos):
#     'The two args are the value and tick position'
#     return '{:.0f}k'.format(x * 1e-10)
# ax.yaxis.set_major_formatter(FixedFormatter([format_thousands(label, _) for _, label in enumerate(ax.get_yticks())]))
profit_diff = merged_df['profit']
categories = merged_df['persian_month']

trace = go.Waterfall(
    x=categories,
    y=profit_diff,
    base=0,
    increasing={'marker': {'color': 'blue'}},
    decreasing={'marker': {'color': 'red'}},
    totals={'marker': {'color': 'blue', 'line': {'color': 'black', 'width': 2}}},
    name='Profit'
)

layout = go.Layout(
    title='Profit Waterfall Plot - Last 6 months',
    xaxis=dict(title='Month'),
    yaxis=dict(title='Profit Value'),
)

fig3 = go.Figure(data=[trace], layout=layout)
fig3.show()

#------------------channel sale pychart----------------------------------
channel=df[df['persian_year']==1401]
channel = df.groupby('Channel')['GMV'].sum().reset_index()

fig4 = px.pie(channel, values='GMV', names='Channel',title='Sale channels')

#------------------------commission barchart-------------------------------------
df_gmv = df[df['persian_year']==1401]
df_gmv = df_gmv.groupby('persian_month')['Commission'].sum().reset_index()

fig5 = go.Figure(data=go.Bar(x=df_gmv['persian_month'], y=df_gmv['Commission']))

fig5.update_layout(
    title='Last year Commission revenue -per month',
    xaxis=dict(title='Month'),
    yaxis=dict(title='Commission Value')
)
fig5.show()

#-------------------------------------------------------------------------
col1, col2, col3 ,col4, col5, col6= st.columns(6)
with col1:
    demand_fig
    fig5
    fig3
with col4:
    fig1
    fig4

