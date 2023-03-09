# imports
import streamlit as st
st.set_page_config(layout="wide", page_title="LAS Explorer v 0.1")
import pandas as pd
import lasio
from io import StringIO
#Plotly imports
import plotly.graph_objects 
from plotly.subplots import make_subplots
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
import chart_studio.plotly as py
#local imports

@st.cache_data
def load_data(uploaded_file):
    if uploaded_file is not None:
        try:
            bytes_data = uploaded_file.read()
            str_io = StringIO(bytes_data.decode('Windows-1252'))
            las_file = lasio.read(str_io)
            well_data = las_file.df()
            well_data['DEPTH'] = well_data.index

        except UnicodeDecodeError as e:
            st.error(f"error loading log.las: {e}")
    else:
        las_file = None
        well_data = None

    return las_file, well_data

# side bar options and file upload
las_file = None
st.sidebar.write('# LAS Data Explorer')
st.sidebar.write("To begin using the app, laod your LAS file")

uploadedfile = st.sidebar.file_uploader(' ', type=['.las'])
las_file, well_data = load_data(uploadedfile)

if las_file:
    st.sidebar.success('File Uploaded Successfully')
    st.sidebar.write(f'<b>Well Name</b>: {las_file.well.WELL.value}',unsafe_allow_html=True)

# home page
def home():
    st.title('LAS Data Explorer - version 0.1')
    st.write('''LAS data explorer tool designed by Olga Bauer BRACS TWDB using Python and Streamlit to view and understand the contents of a LAS file.''')
    st.write('\n')

# header
def header(las_file):
    st.title("LAS header info")
    if not las_file:
        st.warning("No file has been uploaded")   
    else:
        for item in las_file.well:
            st.write(f"<b>{item.descr.capitalize()} ({item.mnemonic}):</b> {item.value}", unsafe_allow_html=True)

# well log measurements
def raw_data(las_file, well_data):
    st.title('LAS File Data Info')
    if not las_file:
        st.warning('No file has been uploaded')
    else:
        st.write('**Curve Information**')
        for count, curve in enumerate(las_file.curves):
            # st.write(f"<b>Curve:</b> {curve.mnemonic}, <b>Units: </b>{curve.unit}, <b>Description:</b> {curve.descr}", unsafe_allow_html=True)
            st.write(f"   {curve.mnemonic} ({curve.unit}): {curve.descr}", unsafe_allow_html=True)
        st.write(f"<b>There are a total of: {count+1} curves present within this file</b>", unsafe_allow_html=True)

        st.write('<b>Curve Statistics</b>', unsafe_allow_html=True)
        st.write(well_data.describe())
        st.write('<b>Raw Data Values</b>', unsafe_allow_html=True)
        st.dataframe(data=well_data)

# well log data with Plotly
def plot(las_file, well_data):
    st.title('LAS File Visualisation')

    if not las_file:
        st.warning('No file has been uploaded')

    else:
        columns = list(well_data.columns)
        st.write('Expand one of the following to visualise your well data.')
        with st.expander('Log Plot'):    
            curves = st.multiselect('Select Curves To Plot', columns)
            if len(curves) <= 1:
                st.warning('Please select at least 2 curves.')
            else:
                curve_index = 1
                fig = plotly.tools.make_subplots(rows=1, cols= len(curves), subplot_titles=curves, shared_yaxes=True)

                for curve in curves:
                    fig.add_trace(go.Scatter(x=well_data[curve], y=well_data['DEPTH']), row=1, col=curve_index)
                    curve_index+=1

                fig.update_layout(height=1000, showlegend=False, yaxis={'title':'DEPTH','autorange':'reversed'})
                fig.layout.template='seaborn'
                st.plotly_chart(fig, use_container_width=True)

        with st.expander('Histograms'):
            col1_h, col2_h = st.beta_columns(2)
            col1_h.header('Options')

            hist_curve = col1_h.selectbox('Select a Curve', columns)
            log_option = col1_h.radio('Select Linear or Logarithmic Scale', ('Linear', 'Logarithmic'))

            if log_option == 'Linear':
                log_bool = False
            elif log_option == 'Logarithmic':
                log_bool = True

            histogram = px.histogram(well_data, x=hist_curve, log_x=log_bool)
            histogram.layout.template='seaborn'
            col2_h.plotly_chart(histogram, use_container_width=True)

        with st.expander('Crossplot'):
            col1, col2 = st.beta_columns(2)
            col1.write('Options')

            xplot_x = col1.selectbox('X-Axis', columns)
            xplot_y = col1.selectbox('Y-Axis', columns)
            xplot_col = col1.selectbox('Color By', columns)
            xplot_x_log = col1.radio('X Axis - Linear or Logarithmic', ('Linear', 'Logarithmic'))
            xplot_y_log = col1.radio('Y Axis - Linear or Logarithmic', ('Linear', 'Logarithmic'))

            if xplot_x_log == 'Linear':
                xplot_x_bool = False
            elif xplot_x_log == 'Logarithmic':
                xplot_x_bool = True

            if xplot_y_log == 'Linear':
                xplot_y_bool = False
            elif xplot_y_log == 'Logarithmic':
                xplot_y_bool = True

            col2.write('Crossplot')

            xplot = px.scatter(well_data, x=xplot_x, y=xplot_y, color=xplot_col, log_x=xplot_x_bool, log_y=xplot_y_bool)
            xplot.layout.template='seaborn'
            col2.plotly_chart(xplot, use_container_width=True)

# Sidebar Navigation
st.sidebar.title('Navigation')
options = st.sidebar.radio('Select a page:', 
    ['Home', 'Header Information', 'Data Information', 'Data Visualisation', 'Missing Data Visualisation'])

if options == 'Home':
    home()
elif options == 'Header Information':
    header(las_file)
elif options == 'Data Information':
    raw_data(las_file, well_data)
elif options == 'Data Visualisation':
    plot(las_file, well_data)
#elif options == 'Missing Data Visualisation':
    #missingdata.missing(las_file, well_data)



