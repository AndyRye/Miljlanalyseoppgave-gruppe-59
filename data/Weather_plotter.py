import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta

from FrostAPI import FrostAPI, DataAnalyse
from weatherapi import WeatherAPI, WeatherDataProcessor, WeatherDataCleaner, WeatherStatistics

st.set_page_config(layout="wide", page_title="Værdata")

def main():
    st.title("Værdata")
    
    with st.sidebar:
        st.header("Værstasjoner")
        data_source = st.radio("velg værstasjon:", ["MET Norway API"])
        
        st.header("tidsperiode")
        today = datetime.now()
        start_date = st.date_input("Start dato", today - timedelta(days=7))
        end_date = st.date_input("Slutt dato", today)
        
        
            
        
        st.header("Location Settings")
        lat = st.number_input("Breddegrader", value=59.9139, format="%.4f")
        lon = st.number_input("Lengdegrader", value=10.7522, format="%.4f")
    
        if st.button("Vis data", type="primary"):
            st.session_state.data_loaded = True
            with st.spinner("Henter data..."):
                # Here you would instantiate and use your API classes
                st.session_state.data_source = "met"
                st.session_state.weather_api_params = {
                    "lat": lat,
                    "lon": lon,
                    "start_date": start_date,
                    "end_date": end_date
                    }
                # Sample data for demonstration
                dates = pd.date_range(start=start_date, end=end_date, freq='H')
                temp_data = np.sin(np.linspace(0, 10, len(dates))) * 8 + 10 + np.random.normal(0, 2, len(dates))
                wind_data = np.abs(np.sin(np.linspace(0, 15, len(dates)))) * 4 + np.random.normal(0, 0.5, len(dates))
                humidity_data = np.random.normal(70, 15, len(dates))
                humidity_data = np.clip(humidity_data, 0, 100)
                
                st.session_state.df = pd.DataFrame({
                    'Tid': dates,
                    'Temperatur (C)': temp_data,
                    'Vindhastighet (m/s)': wind_data,
                    'Luftfuktighet(%)': humidity_data,
                    'Lufttrykk(hPa)': np.random.normal(1013, 5, len(dates)),
                    'Skydekke(%)': np.random.uniform(0, 100, len(dates))
                })
                st.session_state.df['Tid'] = pd.to_datetime(st.session_state.df['Tid'])
                st.session_state.df.set_index('Tid', inplace=True)

    # Main content area
    if 'data_loaded' in st.session_state and st.session_state.data_loaded:
        display_dashboard()
    else:
        st.info("Velg kilde og trykk på 'vis data' for å starte")
        # Display sample visualizations as placeholders
        display_sample_visualizations()

def display_dashboard():
    df = st.session_state.df
    
    # Overview metrics
    st.header("Oversikt")
    col1, col2, col3, col4 = st.columns(4)
    
    if st.session_state.data_source == "frost":
        with col1:
            st.metric("Average Temperature", f"{df['temperatur'].mean():.1f}°C", 
                     f"{df['temperatur'].mean() - df['temperatur'].iloc[0]:.1f}°C")
        with col2:
            if 'pm10' in df.columns and df['pm10'].notna().any():
                st.metric("Average PM10", f"{df['pm10'].mean():.1f} µg/m³", 
                         f"{df['pm10'].mean() - df['pm10'].iloc[0]:.1f}")
        with col3:
            if 'pm2_5' in df.columns and df['pm2_5'].notna().any():
                st.metric("Average PM2.5", f"{df['pm2_5'].mean():.1f} µg/m³", 
                         f"{df['pm2_5'].mean() - df['pm2_5'].iloc[0]:.1f}")
    else:  # MET API
        with col1:
            st.metric("Average Temperature", f"{df['Temperatur (C)'].mean():.1f}°C", 
                     f"{df['Temperatur (C)'].mean() - df['Temperatur (C)'].iloc[0]:.1f}°C")
        with col2:
            st.metric("Average Wind Speed", f"{df['Vindhastighet (m/s)'].mean():.1f} m/s", 
                     f"{df['Vindhastighet (m/s)'].mean() - df['Vindhastighet (m/s)'].iloc[0]:.1f}")
        with col3:
            st.metric("Average Humidity", f"{df['Luftfuktighet(%)'].mean():.1f}%", 
                     f"{df['Luftfuktighet(%)'].mean() - df['Luftfuktighet(%)'].iloc[0]:.1f}")
        with col4:
            st.metric("Average Air Pressure", f"{df['Lufttrykk(hPa)'].mean():.1f} hPa", 
                     f"{df['Lufttrykk(hPa)'].mean() - df['Lufttrykk(hPa)'].iloc[0]:.1f}")
    
    # Time series tab and statistical analysis tab
    tab1, tab2, tab3 = st.tabs(["Time Series Analysis", "Statistical Analysis", "Data Correlations"])
    
    with tab1:
        st.subheader("Time Series Analysis")
        
        # Time resolution selector
        resolution = st.selectbox(
            "Select Time Resolution",
            ["Raw Data", "Hourly Average", "Daily Average", "Weekly Average"],
            index=0
        )
        
        # Resample data based on selected resolution
        if resolution == "Hourly Average":
            plot_df = df.resample('H').mean()
        elif resolution == "Daily Average":
            plot_df = df.resample('D').mean()
        elif resolution == "Weekly Average":
            plot_df = df.resample('W').mean()
        else:
            plot_df = df
        
        # Create interactive time series plots
        if st.session_state.data_source == "frost":
            if 'stasjon' in df.columns:
                stations = df['stasjon'].unique()
                selected_station = st.selectbox("Select Station", stations)
                station_df = df[df['stasjon'] == selected_station]
            else:
                station_df = df
                
            fig = make_subplots(rows=3, cols=1, 
                               subplot_titles=("Temperature", "PM10", "PM2.5"),
                               shared_xaxes=True, 
                               vertical_spacing=0.1,
                               specs=[[{"type": "scatter"}], 
                                      [{"type": "scatter"}],
                                      [{"type": "scatter"}]])
            
            fig.add_trace(
                go.Scatter(x=station_df.index, y=station_df['temperatur'], mode='lines', name='Temperature'),
                row=1, col=1
            )
            
            if 'pm10' in station_df.columns and station_df['pm10'].notna().any():
                fig.add_trace(
                    go.Scatter(x=station_df.index, y=station_df['pm10'], mode='lines', name='PM10'),
                    row=2, col=1
                )
            
            if 'pm2_5' in station_df.columns and station_df['pm2_5'].notna().any():
                fig.add_trace(
                    go.Scatter(x=station_df.index, y=station_df['pm2_5'], mode='lines', name='PM2.5'),
                    row=3, col=1
                )
                
        else:  # MET API
            # Create time series visualization for weather data
            fig = make_subplots(rows=3, cols=1, 
                               subplot_titles=("Temperature", "Wind Speed", "Humidity"),
                               shared_xaxes=True, 
                               vertical_spacing=0.1)
            
            fig.add_trace(
                go.Scatter(x=plot_df.index, y=plot_df['Temperatur (C)'], mode='lines', name='Temperature'),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Scatter(x=plot_df.index, y=plot_df['Vindhastighet (m/s)'], mode='lines', name='Wind Speed'),
                row=2, col=1
            )
            
            fig.add_trace(
                go.Scatter(x=plot_df.index, y=plot_df['Luftfuktighet(%)'], mode='lines', name='Humidity'),
                row=3, col=1
            )
        
        fig.update_layout(height=800, showlegend=True)
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.subheader("Statistical Analysis")
        
        if st.session_state.data_source == "frost":
            columns_to_analyze = [col for col in ['temperatur', 'pm10', 'pm2_5'] if col in df.columns]
        else:  # MET API
            columns_to_analyze = ['Temperatur (C)', 'Vindhastighet (m/s)', 'Luftfuktighet(%)', 'Lufttrykk(hPa)', 'Skydekke(%)']
        
        selected_column = st.selectbox("Select Parameter for Analysis", columns_to_analyze)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Histogram
            fig = px.histogram(df, x=selected_column, nbins=30, marginal="box", 
                          title=f"Distribution of {selected_column}")
            st.plotly_chart(fig, use_container_width=True)
            
            # Statistics table
            stats = {
                "Mean": df[selected_column].mean(),
                "Median": df[selected_column].median(),
                "Std Dev": df[selected_column].std(),
                "Min": df[selected_column].min(),
                "Max": df[selected_column].max(),
                "Skewness": df[selected_column].skew(),
                "Kurtosis": df[selected_column].kurtosis()
            }
            st.dataframe(pd.DataFrame([stats]), use_container_width=True)
        
        with col2:
            # Box plot by time period
            if st.session_state.data_source == "frost" and 'stasjon' in df.columns:
                fig = px.box(df, x='stasjon', y=selected_column, 
                         title=f"Box Plot of {selected_column} by Station")
            else:
                # Group by day of week for temporal patterns
                df_copy = df.copy()
                df_copy['day_of_week'] = df_copy.index.day_name()
                day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                fig = px.box(df_copy, x='day_of_week', y=selected_column, 
                         category_orders={"day_of_week": day_order},
                         title=f"Box Plot of {selected_column} by Day of Week")
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Show outliers
            z_threshold = 2.5
            outliers = df[abs((df[selected_column] - df[selected_column].mean()) / df[selected_column].std()) > z_threshold]
            st.write(f"Outliers (Z-score > {z_threshold}):")
            if not outliers.empty:
                st.dataframe(outliers[[selected_column]], use_container_width=True)
            else:
                st.write("No significant outliers detected.")

    with tab3:
        st.subheader("Data Correlations")
        
        if st.session_state.data_source == "frost":
            corr_columns = [col for col in ['temperatur', 'pm10', 'pm2_5'] if col in df.columns and df[col].notna().any()]
        else:  # MET API
            corr_columns = ['Temperatur (C)', 'Vindhastighet (m/s)', 'Luftfuktighet(%)', 'Lufttrykk(hPa)', 'Skydekke(%)']
        
        if len(corr_columns) > 1:
            corr_matrix = df[corr_columns].corr()
            
            # Heatmap
            fig = px.imshow(corr_matrix, 
                         text_auto=True, 
                         color_continuous_scale='RdBu_r',
                         title="Correlation Matrix")
            st.plotly_chart(fig, use_container_width=True)
            
            # Scatter plots for selected parameters
            st.subheader("Relationship Explorer")
            col1, col2 = st.columns(2)
            with col1:
                param1 = st.selectbox("Select first parameter", corr_columns, index=0)
            with col2:
                remaining_cols = [col for col in corr_columns if col != param1]
                param2 = st.selectbox("Select second parameter", remaining_cols, 
                                     index=0 if remaining_cols and remaining_cols[0] != param1 else (1 if len(remaining_cols) > 1 else 0))
            
            fig = px.scatter(df, x=param1, y=param2, 
                          trendline="ols", 
                          title=f"Relationship between {param1} and {param2}")
            st.plotly_chart(fig, use_container_width=True)
            
            # Show correlation stats
            corr_value = corr_matrix.loc[param1, param2]
            st.info(f"Correlation coefficient: {corr_value:.3f}")
            
            if abs(corr_value) > 0.7:
                st.success("Strong correlation detected!")
            elif abs(corr_value) > 0.3:
                st.info("Moderate correlation detected.")
            else:
                st.warning("Weak correlation detected.")
        else:
            st.info("Not enough data columns available for correlation analysis.")

    # Data table (collapsible)
    with st.expander("View Raw Data"):
        st.dataframe(df, use_container_width=True)
        
        csv = df.to_csv().encode('utf-8')
        st.download_button(
            label="Download data as CSV",
            data=csv,
            file_name='weather_data.csv',
            mime='text/csv',
        )

def display_sample_visualizations():
    # Display placeholder charts
    st.subheader("Sample Visualizations (Select data source to see actual data)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        dates = pd.date_range(start='2023-01-01', periods=100, freq='H')
        temp_data = np.sin(np.linspace(0, 10, 100)) * 5 + 15 + np.random.normal(0, 1, 100)
        df = pd.DataFrame({'date': dates, 'temperature': temp_data})
        
        fig = px.line(df, x='date', y='temperature', title="Sample Temperature Data")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.histogram(df, x='temperature', title="Sample Distribution")
        st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()



    





