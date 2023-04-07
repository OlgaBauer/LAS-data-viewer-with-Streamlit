# imports
import streamlit as st
import pandas as pd
import lasio
from io import StringIO

#Plotly imports
import plotly.graph_objects 
from plotly.subplots import make_subplots
import plotly.express as px
import plotly.graph_objects as go

# web page set up
st.set_page_config(layout="wide", page_title="LAS Explorer v 0.3")

# creating the load_data function
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

# adding side bar 
las_file = None

st.sidebar.write('# LAS Data Explorer')
st.sidebar.write("To begin using the app, laod your LAS file")

# adding file uploader
uploadedfile = st.sidebar.file_uploader(' ', type=['.las'])
las_file, well_data = load_data(uploadedfile)

if las_file:
    st.sidebar.success('File Uploaded Successfully')
    st.sidebar.write(f'<b>Well Name</b>: {las_file.well.WELL.value}',unsafe_allow_html=True)

# adding home page
def home():
    st.title('LAS Data Explorer - version 0.3')
    st.write('### by Olga Bauer')
    st.write('''LAS Data Explorer is a tool designed using Python and Streamlit to help you view and gain an understanding of the contents of
    a LAS file.''')
    st.write('To begin using the app, load your LAS file using the file upload option on the sidebar. Once you have done this, you can navigate to the relevant tools using the Navigation menu.')
    st.write('\n')
    st.write('## Sections')
    st.write('**Header Information:** Information from the LAS file header.')
    st.write('**Data Information:** Information about the curves contained within the LAS file, including names, statisics and raw data values.')
    st.write('**Data Visualisation:** Visualisation tools to view las file data on a log plot, crossplot and histogram.')
    st.write('**Missing Data Visualisation:** Visualisation tools understand data extent and identify areas of missing values.')

# header
def header(las_file):
    st.title("Well Header Information")
    if not las_file:
        st.warning("No file has been uploaded")   
    else:
        for item in las_file.well:
            st.write(f"<b>{item.descr.capitalize()}:</b> {item.value}", unsafe_allow_html=True)
            #({item.mnemonic}) removed

# well log measurements
def raw_data(las_file, well_data):
    st.title('Well Log Measurement Information')
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
            col1_h, col2_h = st.columns(2)
            col1_h.header('Options')

            hist_curve = col1_h.selectbox('Select a Curve', columns)
            #log_option = col1_h.radio('Select Linear or Logarithmic Scale', ('Linear', 'Logarithmic'))
            hist_col = col1_h.color_picker('Select Histogram Colour')
            st.write('Color is'+hist_col)

            # removed the Logaritmic scale 
            #if log_option == 'Linear':
                #log_bool = False
            #elif log_option == 'Logarithmic':
                #log_bool = True

            histogram = px.histogram(well_data, x=hist_curve)
            histogram.update_traces(marker_color=hist_col)
            histogram.layout.template='seaborn'
            col2_h.plotly_chart(histogram, use_container_width=True)

        with st.expander('Crossplot'):
            col1, col2 = st.columns(2)
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

# Missing data
def missing(las_file, well_data):
    st.title('LAS File Missing Data')
    
    if not las_file:
        st.warning('No file has been uploaded')
    
    else:
        st.write("""The following plot can be used to identify the depth range of each of the logging curves.""")

        data_nan = well_data.notnull().astype('int')
        # Need to setup an empty list for len check to work
        curves = []
        columns = list(well_data.columns)
        columns.pop(-1) #pop off depth

        min_depth = well_data['DEPTH'].min()
        max_depth = well_data['DEPTH'].max()

        col1_md, col2_md, col3_md, col4_md = st.columns(4)

        selection = col1_md.radio('Select all data or custom selection', ('All Data', 'Custom Selection'))
        fill_color_md = col2_md.color_picker('Select Fill Colour', '#9D0000')
        top_depth = col3_md.number_input('Top Depth', value=min_depth)
        bottom_depth = col4_md.number_input('Bottom Depth', value=max_depth)

        if selection == 'All Data':
            curves = columns
        else:
            curves = st.multiselect('Select Curves To Plot', columns)

        if len(curves) <= 1:
            st.warning('Please select at least 2 curves.')
        else:
            curve_index = 1
            fig = make_subplots(rows=1, cols= len(curves), subplot_titles=curves, shared_yaxes=True, horizontal_spacing=0.02)

            for curve in curves:
                fig.add_trace(go.Scatter(x=data_nan[curve], y=well_data['DEPTH'], 
                    fill='tozerox',line=dict(width=0), fillcolor=fill_color_md), row=1, col=curve_index)
                fig.update_xaxes(range=[0, 1], visible=False)
                fig.update_xaxes(range=[0, 1], visible=False)
                curve_index+=1
            
            fig.update_layout(height=1000, showlegend=False, yaxis={'title':'DEPTH','autorange':'reversed'})
            # rotate all the subtitles of 90 degrees
            for annotation in fig['layout']['annotations']: 
                    annotation['textangle']=-90
            fig.layout.template='seaborn'
            st.plotly_chart(fig, use_container_width=True)

# Sidebar Navigation
st.sidebar.title('Navigation')
options = st.sidebar.radio('Select a section:', 
    ['Home', 'Header Information', 'Data Information', 'Data Visualisation', 'Missing Data Visualisation'])

if options == 'Home':
    home()
elif options == 'Header Information':
    header(las_file)
elif options == 'Data Information':
    raw_data(las_file, well_data)
elif options == 'Data Visualisation':
    plot(las_file, well_data)
elif options == 'Missing Data Visualisation':
    missing(las_file, well_data)
