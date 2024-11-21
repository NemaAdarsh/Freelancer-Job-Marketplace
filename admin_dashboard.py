import streamlit as st
import mysql.connector
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd



# Page configuration MUST be the first Streamlit command
st.set_page_config(
    page_title="Freelance Platform Dashboard",
    page_icon="🚀",
    layout="wide"
)

# MySQL Database connection
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="dbmsproject"
    )

# Custom CSS for a futuristic look
st.markdown("""
    <style>
        .stApp {
            background-color: #0f1729;
            color: #e0e6f3;
        }
        .stTitle {
            color: #4ecdc4 !important;
            font-size: 2.5rem !important;
            text-align: center;
            text-shadow: 0 0 10px rgba(78, 205, 196, 0.5);
        }
        .stTabs [data-baseweb="tab-list"] {
            background-color: #1a2747;
            border-radius: 15px;
        }
        .stTabs [data-baseweb="tab"] {
            color: #4ecdc4;
            padding: 10px 20px;
            transition: all 0.3s ease;
        }
        .stTabs [data-baseweb="tab"]:hover {
            background-color: #2a3d5a;
        }
        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            background-color: #4ecdc4;
            color: #0f1729;
        }
        .stTextInput > div > div > input {
            background-color: #1a2747;
            color: #e0e6f3;
            border: 1px solid #4ecdc4;
        }
        .stButton > button {
            background-color: #4ecdc4 !important;
            color: #0f1729 !important;
            border: none;
            border-radius: 10px;
            transition: all 0.3s ease;
        }
        .stButton > button:hover {
            background-color: #3aa69b !important;
            transform: scale(1.05);
        }
    </style>
""", unsafe_allow_html=True)

# Streamlit App
st.title("Freelance Platform Dashboard")

# Tab-based navigation
tab1, tab2 = st.tabs(["👥 User Management", "📊 Platform Analytics"])

# Add Users Section
with tab1:
    st.header("User Registration")
    
    # User type selection
    user_type = st.radio("Select User Type", ["Freelancer", "Client"], horizontal=True)

    # Freelancer Form
    if user_type == "Freelancer":
        with st.form("freelancer_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Full Name", placeholder="John Doe")
                email = st.text_input("Email", placeholder="john.doe@example.com")
            with col2:
                phone = st.text_input("Phone", placeholder="1234567890")
                skills = st.text_input("Skills", placeholder="Web Dev, Design")
            
            rating = st.slider("Rating", 0.0, 5.0, 4.0)
            is_available = st.toggle("Currently Available")

            submitted = st.form_submit_button("Register Freelancer")
            if submitted:
                try:
                    db = connect_db()
                    cursor = db.cursor()
                    query = """
                        INSERT INTO freelancer (name, email, phone, skills, rating, is_available)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(query, (name, email, phone, skills, rating, int(is_available)))
                    db.commit()
                    st.success("Freelancer registered successfully!")
                except Exception as e:
                    st.error(f"Registration failed: {e}")
                finally:
                    cursor.close()
                    db.close()

    # Client Form
    else:
        with st.form("client_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Full Name", placeholder="Jane Smith")
                email = st.text_input("Email", placeholder="jane.smith@company.com")
            with col2:
                phone = st.text_input("Phone", placeholder="9876543210")
                company_name = st.text_input("Company", placeholder="TechCorp")
            
            posted_jobs = st.number_input("Jobs Posted", min_value=0, step=1)

            submitted = st.form_submit_button("Register Client")
            if submitted:
                try:
                    db = connect_db()
                    cursor = db.cursor()
                    query = """
                        INSERT INTO client (name, email, phone, company_name, posted_jobs)
                        VALUES (%s, %s, %s, %s, %s)
                    """
                    cursor.execute(query, (name, email, phone, company_name, posted_jobs))
                    db.commit()
                    st.success("Client registered successfully!")
                except Exception as e:
                    st.error(f"Registration failed: {e}")
                finally:
                    cursor.close()
                    db.close()

# View Stats Section
with tab2:
    st.header("Platform Insights")

    def get_stats():
        db = connect_db()
        cursor = db.cursor(dictionary=True)

        stats = {}
        cursor.execute("SELECT COUNT(*) AS total_clients FROM client")
        stats['total_clients'] = cursor.fetchone()['total_clients']

        cursor.execute("SELECT COUNT(*) AS total_freelancers FROM freelancer")
        stats['total_freelancers'] = cursor.fetchone()['total_freelancers']

        cursor.execute("SELECT COUNT(*) AS total_jobs FROM jobs")
        stats['total_jobs'] = cursor.fetchone()['total_jobs']

        cursor.execute("SELECT COUNT(*) AS open_jobs FROM jobs WHERE status = 'Open'")
        stats['open_jobs'] = cursor.fetchone()['open_jobs']

        cursor.execute("SELECT COUNT(*) AS completed_contracts FROM contracts WHERE status = 'Completed'")
        stats['completed_contracts'] = cursor.fetchone()['completed_contracts']

        cursor.execute("SELECT SUM(payment) AS total_payment FROM contracts WHERE status = 'Completed'")
        stats['total_payment'] = cursor.fetchone()['total_payment'] or 0

        cursor.execute("SELECT AVG(rating) AS avg_rating FROM freelancer WHERE rating IS NOT NULL")
        stats['avg_freelancer_rating'] = cursor.fetchone()['avg_rating']

        cursor.close()
        db.close()

        return stats

    # Fetch stats
    stats = get_stats()

    # Create columns for visualizations
    col1, col2 = st.columns(2)

    # User Distribution Pie Chart
    with col1:
        labels = ['Clients', 'Freelancers']
        values = [stats['total_clients'], stats['total_freelancers']]
        fig1 = go.Figure(data=[go.Pie(
            labels=labels, 
            values=values, 
            marker_colors=['#4ecdc4', '#ff6b6b'],
            textinfo='value+percent',
            hole=.4
        )])
        fig1.update_layout(
            title_text="User Distribution",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#e0e6f3'
        )
        st.plotly_chart(fig1)

    # Job Status Bar Chart
    with col2:
        job_data = {
            'Status': ['Total Jobs', 'Open Jobs', 'Completed Contracts'],
            'Count': [stats['total_jobs'], stats['open_jobs'], stats['completed_contracts']]
        }
        fig2 = px.bar(
            job_data, 
            x='Status', 
            y='Count', 
            color_discrete_sequence=['#4ecdc4'],
            title='Job Status Overview'
        )
        fig2.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#e0e6f3'
        )
        st.plotly_chart(fig2)

    # Key Metrics
    st.subheader("Key Metrics")
    metrics_cols = st.columns(3)
    metrics_cols[0].metric("Total Payment", f"${stats['total_payment']:.2f}", "Platform Revenue")
    metrics_cols[1].metric("Avg Freelancer Rating", f"{stats['avg_freelancer_rating']:.2f}/5.0", "Performance")
    metrics_cols[2].metric("Open Jobs", stats['open_jobs'], "Current Opportunities")
