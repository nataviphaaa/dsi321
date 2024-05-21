import streamlit as st
import pandas as pd
import sqlalchemy
import altair as alt
from io import StringIO

# Connection string to the PostgreSQL database
DATABASE_URL = "postgresql+psycopg2://postgres:1234@192.168.1.101:5432/postgres"
# DATABASE_URL = "postgresql+psycopg2://user:password@localhost:5432/datascience"

st.set_page_config(page_title='มูลนิธิสดศรี-สฤษดิ์วงศ์', layout='wide', page_icon='images/index.png')

st.markdown(
    """
    <style>
    .main {
        background: linear-gradient(135deg, #ffffff 50%, #ffffff 50%);
        background-size: cover;
    }
    .title{
    font-size: 24px;
    font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Header
t1, t2 = st.columns((0.07, 0.4))
t1.image('images/index.png', width=120)
t2.title("มูลนิธิสดศรี-สฤษดิ์วงศ์")
t2.markdown(" **โทรศัพท์:** 02-511-5855 **| เว็บไซต์:** https://thaissf.org")

# Setup database connection
@st.cache_resource
def get_database_connection():
    engine = sqlalchemy.create_engine(DATABASE_URL)
    return engine.connect()

# Fetch dataset names from the database
@st.cache_data
def get_datasets(_conn):
    query = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
    return pd.read_sql(query, _conn)

# Fetch metadata for a specific table
@st.cache_data
def get_table_description(_conn, table_name):
    query = f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table_name}'"
    return pd.read_sql(query, _conn)

# Load data from a specific table
@st.cache_data
def load_data(_conn, table_name):
    query = f"SELECT * FROM {table_name}"
    return pd.read_sql(query, _conn)

# Function to create bar chart for dataset1
def bar_dataset1(_conn):
    query = """
    SELECT เขตการศึกษา, COUNT(เขตการศึกษา) AS count 
    FROM dataset1 
    WHERE เขตการศึกษา IS NOT NULL AND เขตการศึกษา != '-'
    GROUP BY เขตการศึกษา
    """
    df = pd.read_sql(query, _conn)
    return df

# Function to create bar chart for dataset2
def bar_dataset2(_conn):
    query = """
    SELECT จังหวัด, เกรดเฉลี่ยสะสม
    FROM dataset2
    WHERE จังหวัด IS NOT NULL 
    AND เกรดเฉลี่ยสะสม IS NOT NULL 
    AND เกรดเฉลี่ยสะสม != '#N/A'
    GROUP BY เกรดเฉลี่ยสะสม
    """
    df = pd.read_sql(query, _conn)
    return df


def main():
    st.markdown("<div class='title'>ข้อมูลผู้สมัครขอรับทุนสมเด็จพระสังฆราชปี พ.ศ.2566</div>", unsafe_allow_html=True)

    conn = get_database_connection()
    datasets = get_datasets(conn)
    dataset_names = datasets['table_name'].tolist()

    if not dataset_names:
        st.error("No datasets found in the database.")
        return

    dataset_selected = st.sidebar.selectbox("Select a dataset", dataset_names)

    if dataset_selected:
        # Display metadata
        metadata = get_table_description(conn, dataset_selected)
        if not metadata.empty:
            st.write(f"Metadata for {dataset_selected}:")
            st.dataframe(metadata)
        else:
            st.write("No metadata available.")

        # Load and display data
        data = load_data(conn, dataset_selected)
        if not data.empty:
            st.write("Data Preview:")
            st.dataframe(data.head())

            if dataset_selected == 'dataset1':
                # Plot bar chart using Altair for dataset1
                st.write("Bar Chart for เขตการศึกษา:")
                bar_data = bar_dataset1(conn)
                st.write("Data Bar:", bar_data)  # Debug statement
                
                chart = alt.Chart(bar_data).mark_bar().encode(
                    x=alt.X('เขตการศึกษา', sort=None),
                    y='count',
                    color=alt.value('steelblue')
                ).properties(
                    title='Bar Chart แสดงจำนวนผู้สมัครขอรับทุน by เขตการศึกษา'
                ).configure_axis(
                    labelColor='black',
                    titleColor='black'
                ).configure_title(
                    color='black'
                )
                
                st.altair_chart(chart, use_container_width=True)

            if dataset_selected == 'dataset2':
                # Plot bar chart using Altair for dataset2
                st.write("Bar Chart for เกรดเฉลี่ยสะสม by จังหวัด:")
                bar_data = bar_dataset2(conn)
                st.write("Data Bar:", bar_data)  # Debug statement
                
                chart = alt.Chart(bar_data).mark_bar().encode(
                    x=alt.X('จังหวัด', sort=None),
                    y='เกรดเฉลี่ยสะสม',
                    color=alt.value('steelblue')
                ).properties(
                    title='เกรดเฉลี่ยสะสม by จังหวัด'
                ).configure_axis(
                    labelColor='black',
                    titleColor='black'
                ).configure_title(
                    color='black'
                )
                
                st.altair_chart(chart, use_container_width=True)

            # Basic EDA options
            if st.button("Show Info"):
                buffer = StringIO()
                data.info(buf=buffer)
                s = buffer.getvalue()
                st.text(s)

            if st.button("Show Distribution"):
                st.write(data.describe())
        else:
            st.write("No data available for this dataset.")

if __name__ == "__main__":
    main()
