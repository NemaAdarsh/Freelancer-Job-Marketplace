import streamlit as st
import mysql.connector
from plyer import notification  # Import plyer for Windows notifications

st.markdown("""
    <style>
        /* Style for the main title */
        .title {
            font-size: 2.5em;
            font-weight: bold;
            color: #007BFF;
            text-align: center;
            margin-bottom: 1em;
        }
        
        /* Style for headers */
        .header {
            font-size: 1.75em;
            font-weight: bold;
            color: #333333;
            margin-top: 1em;
            margin-bottom: 0.5em;
        }
        
        /* Style for subheaders */
        .subheader {
            font-size: 1.3em;
            color: #555555;
            margin-bottom: 0.5em;
        }
        
        /* Style for buttons */
        .stButton button {
            background-color: #28a745;
            color: white;
            font-size: 1em;
            padding: 0.6em 1.2em;
            border-radius: 8px;
            transition: background-color 0.3s ease;
        }
        .stButton button:hover {
            background-color: #218838;
        }
        
        /* Style for sidebar */
        .css-1d391kg {
            background-color: #f0f2f6;
        }
        
        /* Style for query information boxes */
        .expander {
            background-color: #e9ecef;
            color: #333;
            border: 1px solid #ccc;
            padding: 0.8em;
            border-radius: 8px;
        }
    </style>
""", unsafe_allow_html=True)


# Initialize session state for tracking proposal acceptance and completed contracts
if 'accepted_proposals' not in st.session_state:
    st.session_state.accepted_proposals = set()

if 'completed_contracts' not in st.session_state:
    st.session_state.completed_contracts = set()

if 'client_authenticated' not in st.session_state:
    st.session_state.client_authenticated = False
if 'client_id' not in st.session_state:
    st.session_state.client_id = None

def show_notification(title, message):
    notification.notify(
        title=title,
        message=message,
        app_name="Freelancer App",
        timeout=10  # Notification disappears after 10 seconds
    )

def get_db_connection():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",
            database="dbmsproject"
        )
    except mysql.connector.Error as err:
        st.error(f"Database connection error: {err}")
        return None

def authenticate_client(email, phone):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM client where email = %s AND phone = %s",(email, phone))
    client= cursor.fetchone()
    connection.close()
    return client

# Login form
def login():
    st.markdown('<div class="title">Client Login</div>', unsafe_allow_html=True)
    
    email = st.text_input("Email")
    phone = st.text_input("Phone", type="password")

    if st.button("Login"):
        client = authenticate_client(email, phone)
        if client:
            st.session_state.client_authenticated = True
            st.session_state.client_id = client['client_id']
            st.session_state.name = client['name']
            st.success(f"Welcome {client['name']}!")
            return True
        else:
            st.error("Invalid email or phone number. Please try again.")
    return False

def complete_contract(contract_id):
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("SELECT job_id, freelancer_id FROM Contracts WHERE id = %s", (contract_id,))
            contract = cursor.fetchone()

            if contract:
                # Update contract status to completed
                cursor.execute("UPDATE Contracts SET status = 'Completed' WHERE id = %s", (contract_id,))
                connection.commit()

                st.success(f"Contract {contract_id} marked as completed!")
                st.session_state.completed_contracts.add(contract_id)
            else:
                st.error("Contract details not found.")
        except mysql.connector.Error as err:
            st.error(f"Error completing contract: {err}")
        finally:
            cursor.close()
            connection.close()

def add_rating(contract_id, rating_score, review_text):
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.callproc("AddRating", [contract_id, rating_score, review_text])
            connection.commit()
            st.success(f"Rating added for contract {contract_id}!")
        except mysql.connector.Error as err:
            st.error(f"Error adding rating: {err}")
        finally:
            cursor.close()
            connection.close()

def display_query_info(query, description):
    """ Display the SQL query and its description in a modal. """
    with st.expander("Show Query", expanded=False):
        st.write(f"**SQL Query:** `{query}`")
        st.write(f"**Description:** {description}")

def reject_proposal(proposal_id):
    connection = get_db_connection()
    if not connection:
        st.error("Database connection error.")
        return
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Update the proposal status to 'Rejected'
        update_query = "UPDATE Proposals SET status = 'Rejected' WHERE id = %s"
        cursor.execute(update_query, (proposal_id,))
        connection.commit()
        st.success(f"Proposal {proposal_id} rejected successfully!")
    
    except mysql.connector.Error as err:
        st.error(f"Error: {err}")
    finally:
        connection.close()

def accept_proposal(proposal_id):
    connection = get_db_connection()
    if not connection:
        st.error("Database connection error.")
        return
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Use our stored procedure instead of direct updates
        cursor.execute("SET @status_message = ''")
        cursor.callproc('accept_proposal', (proposal_id, '@status_message'))
        
        # Get the status message
        cursor.execute("SELECT @status_message as message")
        result = cursor.fetchone()
        status_message = result['message']
        
        connection.commit()
        
        if 'success' in status_message.lower():
            st.success(status_message)
            show_notification("Attention Freelancer:", "Your Proposal has been Accepted")
        else:
            st.error(status_message)
            
    except mysql.connector.Error as err:
        st.error(f"Error: {err}")
    finally:
        connection.close()

def post_job_and_review_proposals():
    st.markdown('<div class="title">Post A New Job</div>', unsafe_allow_html=True)
    client_id = st.number_input("Client ID", min_value=1, step=1)
    title = st.text_input("Job Title")
    description = st.text_area("Description")
    category = st.selectbox("Category", ["Web Development", "Graphic Design", "Writing"])
    budget = st.number_input("Budget", min_value=1.0)
    deadline = st.date_input("Deadline")
    skills = st.text_input("Required Skills (comma-separated)")

    if st.button("Post Job"):
        query = """
            INSERT INTO Jobs (title, description, category, budget, deadline, required_skills, status, client_id)
            VALUES (%s, %s, %s, %s, %s, %s, 'Open', %s)
        """
        if st.button("Show Query Info for Post Job"):
            display_query_info(query, "This query inserts a new job posting into the Jobs table.")
        
        try:
            connection = get_db_connection()
            if connection:
                cursor = connection.cursor()
                cursor.execute(query, (title, description, category, budget, deadline, skills, client_id))
                connection.commit()
                cursor.close()
                connection.close()
                st.success("Job posted successfully!")
                show_notification("Attention Freelancer:", "A new Job has been Posted")
        except mysql.connector.Error as err:
            st.error(f"Error: {err}")

    # Display proposals for review immediately below the job posting section
    st.markdown('<div class="title">Review Proposals for Your Posted Jobs</div>', unsafe_allow_html=True)
    if client_id > 0:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM Proposals WHERE job_id IN (SELECT id FROM Jobs WHERE client_id = %s)", (client_id,))
            proposals = cursor.fetchall()
            connection.close()

            if proposals:
                for proposal in proposals:
                    st.subheader(f"Proposal for Job ID: {proposal['job_id']}")
                    st.write(f"Cover Letter: {proposal['cover_letter']}")
                    st.write(f"Proposed Rate: {proposal['proposed_rate']}")

                    if proposal['id'] in st.session_state.accepted_proposals:
                        st.success("Proposal already accepted!")
                    else:
                        # Accept proposal button
                        if st.button("Accept Proposal", key=f"accept_{proposal['id']}"):
                            query = "UPDATE Proposals SET status = 'Accepted' WHERE id = %s"
                            display_query_info(query, "This query updates the proposal status to accepted.")
                            st.session_state.accepted_proposals.add(proposal['id'])
                            accept_proposal(proposal['id'])
                            

                        # Reject proposal button
                        if st.button("Reject Proposal", key=f"reject_{proposal['id']}"):
                            reject_proposal(proposal['id'])
                            
def review_contracts():
    st.markdown('<div class="title">Review and Complete Contracts</div>', unsafe_allow_html=True)
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Contracts WHERE status = 'In Progress'")
        contracts = cursor.fetchall()
        connection.close()

        for contract in contracts:
            st.subheader(f"Contract ID: {contract['id']} for Job ID: {contract['job_id']}")
            if st.button("Complete Contract", key=f"complete_{contract['id']}"):
                query = "UPDATE Contracts SET status = 'Completed' WHERE id = %s"
                display_query_info(query, "This query marks the contract as completed.")
                complete_contract(contract['id'])

def rate_completed_contracts():
    st.markdown('<div class="title">Rate Completed Contracts</div>', unsafe_allow_html=True)
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Contracts WHERE status = 'Completed'")
        contracts = cursor.fetchall()
        connection.close()

        for contract in contracts:
            st.subheader(f"Rate Contract ID: {contract['id']}")
            rating_score = st.slider("Rating Score", 1, 5, 3, key=f"rating_{contract['id']}")
            review_text = st.text_area("Review Text", key=f"review_{contract['id']}")
            if st.button("Submit Rating", key=f"submit_rating_{contract['id']}"):
                query = "CALL AddRating(%s, %s, %s)"
                display_query_info(query, "This query calls the stored procedure to add a rating and review for the completed contract.")
                add_rating(contract['id'], rating_score, review_text)
                show_notification("Attention Freelancer:", "Your work has been rated!")








if not st.session_state.client_authenticated:
    if login():
        st.rerun()
else:
    st.image("Client.png", use_column_width=True)  # Replace with your banner image path





    post_job_and_review_proposals()
    review_contracts()
    rate_completed_contracts()
