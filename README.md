# Freelancer Job Marketplace

The **Freelancer Job Marketplace** is a comprehensive web-based platform designed to connect freelancers with clients who require specialized skills for various projects. Unlike traditional employment platforms, this marketplace focuses on facilitating short-term, project-based work. It allows businesses to quickly find expert talent and provides freelancers with access to a wide array of job opportunities. The platform is intuitive and secure, ensuring a seamless experience for both clients and freelancers.

---

## Key Features
- **Clients** can post jobs, manage proposals, and hire freelancers.
- **Freelancers** can create profiles, browse job postings, and submit proposals.
- **Admin Dashboard** provides tools for platform management and user monitoring.
- Secure payments and transparent reviews to build trust among users.
- Real-time dashboards powered by Streamlit for data-driven decision-making.

---

## Prerequisites
Ensure you have the following installed:
1. Python 3.8 or higher
2. Streamlit
3. MySQL
4. Docker (optional for Docker Compose setup)

---

## Getting Started

### Clone the Repository

### Set Up the MySQL Database
1. Start your MySQL server.
2. Create a new database for the application:
   ```sql
   CREATE DATABASE freelancer_job_marketplace;
   ```
3. Import the provided SQL file to set up the tables and initial data:
   ```bash
   mysql -u <username> -p freelancer_job_marketplace < database_setup.sql
   ```
   Replace `<username>` with your MySQL username and `database_setup.sql` with the name of the provided SQL file.

4. Update the database credentials in the application files (if necessary) to match your MySQL setup.

### Run Using Streamlit
The platform is divided into three dashboards: **Freelancer**, **Client**, and **Admin**. Each dashboard can be run independently.

1. Run the **Freelancer Dashboard**:
   ```bash
   streamlit run freelancer_dashboard.py --server.port=8501
   ```
2. Run the **Client Dashboard**:
   ```bash
   streamlit run client_dashboard.py --server.port=8502
   ```
3. Run the **Admin Dashboard**:
   ```bash
   streamlit run admin_dashboard.py --server.port=8503
   ```

### Run Using Docker Compose
Alternatively, you can use Docker Compose to set up and run all dashboards along with the MySQL database:
1. Build and run the containers:
   ```bash
   docker-compose up --build
   ```
2. Access the dashboards at:
   - Freelancer Dashboard: `http://localhost:8501`
   - Client Dashboard: `http://localhost:8502`
   - Admin Dashboard: `http://localhost:8503`

---

## Directory Structure
```plaintext
.
├── freelancer_dashboard.py  # Streamlit app for freelancers
├── client_dashboard.py      # Streamlit app for clients
├── admin_dashboard.py       # Streamlit app for admin
├── database_setup.sql       # SQL file to set up MySQL database
├── docker-compose.yml       # Docker Compose configuration
├── requirements.txt         # Python dependencies
└── README.md                # Documentation
```

---

## Technologies Used
- **Frontend**: Streamlit
- **Backend**: Python
- **Database**: MySQL
- **Deployment**: Docker (optional)

---

## Future Enhancements
- Adding chat functionality for real-time communication.
- AI-based recommendation systems for job-freelancer matching.
- Multi-language support for broader accessibility.

---

## Contributing
Contributions are welcome! Please fork the repository and submit a pull request for review.

Screenshots are provided in the Screenshots Folder.
