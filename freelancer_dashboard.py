import streamlit as st
import mysql.connector
from plyer import notification
import plotly.express as px
import pandas as pd

class DatabaseManager:
    @staticmethod
    def get_connection():
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",
            database="dbmsproject"
        )

class SessionManager:
    @staticmethod
    def initialize_states():
        default_states = {
            'proposal_submitted': set(),
            'completed_jobs': set(),
            'job_to_complete': None,
            'freelancer_authenticated': False,
            'freelancer_id': None
        }
        for key, value in default_states.items():
            if key not in st.session_state:
                st.session_state[key] = value

class AuthenticationService:
    @staticmethod
    def authenticate_freelancer(email, phone):
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM freelancer WHERE email = %s AND phone = %s", (email, phone))
        freelancer = cursor.fetchone()
        connection.close()
        return freelancer

class NotificationService:
    @staticmethod
    def show_notification(title, message):
        notification.notify(
            title=title,
            message=message,
            app_name="Freelancer App",
            timeout=10
        )

class JobService:
    @staticmethod
    def browse_jobs():
        st.markdown('<div class="title">Browse Available Jobs</div>', unsafe_allow_html=True)
        connection = DatabaseManager.get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Jobs WHERE status='Open'")
        jobs = cursor.fetchall()
        connection.close()

        for job in jobs:
            st.subheader(job['title'])
            st.write(f"**Budget:** {job['budget']} | **Deadline:** {job['deadline']}")
            st.write(job['description'])

            if st.button("Apply", key=f"apply_{job['id']}"):
                st.session_state.selected_job_id = job['id']
                st.session_state.proposal_submitted = False

    @staticmethod
    def submit_proposal(job_id):
        st.markdown('<div class="title">Submit A Proposal</div>', unsafe_allow_html=True)

        cover_letter = st.text_area("Cover Letter", height=150)
        proposed_rate = st.number_input("Proposed Rate", min_value=1.0, format="%.2f")
        estimated_time = st.number_input("Estimated Completion Time (days)", min_value=1)

        if st.button("Submit Proposal", key=f"submit_proposal_{job_id}"):
            if not st.session_state.proposal_submitted:
                try:
                    connection = DatabaseManager.get_connection()
                    cursor = connection.cursor()
                    query = """
                        INSERT INTO Proposals (job_id, cover_letter, proposed_rate, estimated_time, freelancer_id, status)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(query, (job_id, cover_letter, proposed_rate, estimated_time, 
                                         st.session_state.freelancer_id, 'Pending'))
                    connection.commit()
                    st.session_state.proposal_submitted = True
                    st.success("Proposal submitted successfully!")
                    NotificationService.show_notification("Proposal Submitted", "Your proposal has been submitted successfully")
                    
                except mysql.connector.Error as err:
                    st.error(f"Database error: {err}")
                finally:
                    cursor.close()
                    connection.close()
            else:
                st.info("Proposal has already been submitted.")

class ContractService:
    @staticmethod
    def view_all_contracts():
        st.markdown('<div class="title">View All Contracts</div>', unsafe_allow_html=True)
        
        try:
            connection = DatabaseManager.get_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT C.*, J.title as job_title 
                FROM Contracts C 
                JOIN Jobs J ON C.job_id = J.id 
                WHERE C.freelancer_id = %s
            """, (st.session_state.freelancer_id,))
            contracts = cursor.fetchall()
            cursor.close()
            connection.close()

            if contracts:
                for contract in contracts:
                    st.subheader(f"Job: {contract['job_title']}")
                    st.write(f"**Agreed Payment:** ${contract['payment']} | **Status:** {contract['status']}")

                    if contract['status'] != 'Completed':
                        if st.button("Complete Job", key=f"complete_{contract['id']}"):
                            st.session_state.job_to_complete = contract['id']
                    else:
                        st.success("Job completed!")
            else:
                st.info("No contracts found.")
                
        except mysql.connector.Error as err:
            st.error(f"Database error: {err}")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")

        if st.session_state.job_to_complete:
            ContractService.complete_contract(st.session_state.job_to_complete)

    @staticmethod
    def complete_contract(contract_id):
        try:
            connection = DatabaseManager.get_connection()
            cursor = connection.cursor()
            query = "UPDATE Contracts SET status = 'Completed' WHERE id = %s"
            cursor.execute(query, (contract_id,))
            connection.commit()
            cursor.close()
            connection.close()
            
            st.success(f"Job ID {contract_id} marked as completed!")
            st.session_state.job_to_complete = None
            st.session_state.completed_jobs.add(contract_id)

        except mysql.connector.Error as err:
            st.error(f"Database error: {err}")

class RatingService:
    @staticmethod
    def view_ratings():
        st.markdown('<div class="title">View All Ratings</div>', unsafe_allow_html=True)
        
        try:
            connection = DatabaseManager.get_connection()
            cursor = connection.cursor(dictionary=True)
            
            cursor.execute(f"SELECT calculate_freelancer_rating({st.session_state.freelancer_id}) as avg_rating")
            avg_rating = cursor.fetchone()['avg_rating']
            
            st.subheader("Your Overall Rating")
            rating_stars = "⭐" * int(avg_rating)
            st.write(f"**Average Rating:** {rating_stars} ({avg_rating:.2f}/5)")
            
            cursor.execute("""
                SELECT R.rating_score, R.review_text, R.rating_date, J.title AS job_title
                FROM ratings R
                JOIN contracts C ON R.contract_id = C.id
                JOIN jobs J ON C.job_id = J.id
                WHERE C.freelancer_id = %s
                ORDER BY R.rating_date DESC
            """, (st.session_state.freelancer_id,))
            ratings = cursor.fetchall()

            if ratings:
                df_ratings = pd.DataFrame(ratings)

                rating_counts = df_ratings['rating_score'].value_counts().sort_index()
                fig = px.bar(rating_counts, x=rating_counts.index, y=rating_counts.values, 
                            labels={'x': 'Rating Score', 'y': 'Count'},
                            title="Your Rating Distribution", 
                            color=rating_counts.index,
                            color_continuous_scale="Viridis")
                st.plotly_chart(fig)

                for rating in ratings:
                    st.subheader(f"Job: {rating['job_title']}")
                    rating_stars = "⭐" * rating['rating_score']
                    st.write(f"**Rating:** {rating_stars} ({rating['rating_score']}/5)")
                    st.write(f"**Review:** {rating['review_text']}")
                    st.write(f"**Date:** {rating['rating_date']}")
                    st.write("---")
            else:
                st.info("No ratings available yet.")
        
        except mysql.connector.Error as err:
            st.error(f"Database error: {err}")
        finally:
            if connection:
                connection.close()

def login():
    st.markdown('<div class="title">Freelancer Login</div>', unsafe_allow_html=True)
    
    email = st.text_input("Email")
    phone = st.text_input("Phone", type="password")

    if st.button("Login"):
        freelancer = AuthenticationService.authenticate_freelancer(email, phone)
        if freelancer:
            st.session_state.freelancer_authenticated = True
            st.session_state.freelancer_id = freelancer['freelancer_id']
            st.session_state.name = freelancer['name']
            st.success(f"Welcome {freelancer['name']}!")
            return True
        else:
            st.error("Invalid email or phone number. Please try again.")
    return False

def main():
    SessionManager.initialize_states()

    # Apply the same Streamlit CSS styling as in the original code
    # Futuristic CSS styles
    st.markdown("""
        <style>
            /* Futuristic Cyberpunk-Inspired Design */
            @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;700&family=Roboto:wght@300;400;700&display=swap');

            :root {
                --primary-color: #00ffff;  /* Bright cyan */
                --secondary-color: #ff00ff;  /* Vibrant magenta */
                --background-dark: #0a0a1a;
                --background-medium: #1a1a2e;
                --text-light: #e0e0ff;
                --accent-glow: rgba(0, 255, 255, 0.3);
            }

            body {
                background-color: var(--background-dark);
                color: var(--text-light);
                font-family: 'Roboto', sans-serif;
                line-height: 1.6;
                overflow-x: hidden;
            }

            .stApp {
                background: linear-gradient(135deg, var(--background-dark) 0%, var(--background-medium) 100%);
            }

            .title {
                font-family: 'Orbitron', sans-serif;
                font-size: 2.5em;
                font-weight: bold;
                color: var(--primary-color);
                text-align: center;
                margin-bottom: 1em;
                text-shadow: 0 0 15px var(--accent-glow);
                letter-spacing: 2px;
                background: linear-gradient(45deg, var(--primary-color), var(--secondary-color));
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }

            .header {
                font-family: 'Orbitron', sans-serif;
                font-size: 1.75em;
                font-weight: 500;
                color: var(--primary-color);
                margin-top: 1em;
                margin-bottom: 0.5em;
                border-bottom: 2px solid var(--primary-color);
                padding-bottom: 0.3em;
            }

            .stButton button {
                background: linear-gradient(45deg, var(--primary-color), var(--secondary-color));
                color: var(--background-dark);
                font-family: 'Orbitron', sans-serif;
                font-size: 1em;
                padding: 0.6em 1.2em;
                border: none;
                border-radius: 20px;
                transition: all 0.3s ease;
                box-shadow: 0 0 15px var(--accent-glow);
                text-transform: uppercase;
                letter-spacing: 1px;
            }

            .stButton button:hover {
                transform: scale(1.05);
                box-shadow: 0 0 25px var(--primary-color);
            }

            .css-1d391kg {
                background: linear-gradient(135deg, var(--background-medium) 0%, var(--background-dark) 100%);
                border-right: 2px solid var(--primary-color);
            }

            .stTextInput input, .stNumberInput input {
                background-color: rgba(26, 26, 46, 0.7);
                border: 2px solid var(--primary-color);
                color: var(--text-light);
                border-radius: 10px;
                transition: all 0.3s ease;
            }

            .stTextInput input:focus, .stNumberInput input:focus {
                border-color: var(--secondary-color);
                box-shadow: 0 0 15px var(--accent-glow);
            }

            .expander {
                background: linear-gradient(145deg, rgba(26, 26, 46, 0.8) 0%, rgba(10, 10, 26, 0.8) 100%);
                border: 2px solid var(--primary-color);
                color: var(--text-light);
                border-radius: 15px;
                padding: 1em;
                box-shadow: 0 0 20px rgba(0, 255, 255, 0.2);
            }

            ::-webkit-scrollbar {
                width: 10px;
            }

            ::-webkit-scrollbar-track {
                background: var(--background-medium);
            }

            ::-webkit-scrollbar-thumb {
                background: var(--primary-color);
                border-radius: 10px;
            }

            ::-webkit-scrollbar-thumb:hover {
                background: var(--secondary-color);
            }

            @media (max-width: 600px) {
                .title {
                    font-size: 2em;
                }
                
                .header {
                    font-size: 1.5em;
                }
            }
        </style>
    """, unsafe_allow_html=True)

    if not st.session_state.freelancer_authenticated:
        if login():
            st.rerun()
    else:
        st.image("Freelancer.png", use_column_width=True)

        menu = st.sidebar.selectbox(
            "Select Section", 
            ["Browse Jobs", "View All Contracts", "View Ratings"]
        )

        if menu == "Browse Jobs":
            JobService.browse_jobs()
            if 'selected_job_id' in st.session_state:
                JobService.submit_proposal(st.session_state.selected_job_id)
        elif menu == "View All Contracts":
            ContractService.view_all_contracts()
        elif menu == "View Ratings":
            RatingService.view_ratings()

if __name__ == "__main__":
    main()