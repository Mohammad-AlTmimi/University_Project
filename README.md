University Project - GPT-Wrapped Academic Assistant

Project Overview

This university project is a GPT-wrapped web application built using FastAPI, designed to assist students in their academic journey by providing support for assessments and answering university-related queries. The application leverages a GPT-based AI model to generate responses, process academic documents, and deliver personalized assistance. It integrates PostgreSQL for structured data, MongoDB for flexible data storage, and MongoDB Atlas for cloud-hosted NoSQL storage with advanced search capabilities. The system is containerized with Docker and deployed on AWS EC2 for scalability and accessibility.

Key features include:





Academic Assessment Support: Helps students with coursework, assignments, and exam preparation through AI-generated responses and document processing.



University Information Queries: Answers questions about university policies, schedules, courses, and more using a GPT model and processed PDF data.



User Management: Supports student signup, login, and profile management.



Chat System: Enables real-time interaction with the GPT model for both authenticated users and guests.



Admin Controls: Allows administrators to manage services, upload course data, process PDFs, and view analytics.
Tech Stack

Backend: Python, FastAPI
Databases:
PostgreSQL: Stores structured data (e.g., users, chats).
MongoDB: Stores unstructured data (e.g., messages, logs).
MongoDB Atlas: Cloud-hosted MongoDB for production-grade scalability and search.


Containerization: Docker, Docker Compose
Deployment: AWS EC2
Other Tools:
Pydantic: Data validation.
SQLAlchemy: PostgreSQL ORM.
PyMongo/Motor: MongoDB client for async operations.
Pandas: Excel file processing.
Pillow: Image processing for profile photos.
SBERT: Sentence-BERT for question classification and embeddings.
Passlib: Password hashing.




Project Architecture
The application follows a microservices-inspired architecture with a single FastAPI service interacting with PostgreSQL and MongoDB databases. It uses Docker for containerization and AWS EC2 for deployment. MongoDB Atlas enables cloud-based data storage and advanced search capabilities (text and vector search).
Key components:

FastAPI Service: Handles API requests, authentication, and business logic.
PostgreSQL: Stores users, chats, and user-portal mappings.
MongoDB (Local): Stores messages and semester courses.
MongoDB Atlas: Stores processed PDF data with text and vector search indexes.
Docker: Ensures consistent environments across development and production.
AWS EC2: Hosts the application for public access.


Prerequisites
To run this project locally, ensure you have:

Python 3.9+
Docker and Docker Compose
AWS CLI (for EC2 deployment)
MongoDB Atlas account with a cluster
PostgreSQL client (optional)
MongoDB Compass (optional)


Project Setup
1. Clone the Repository
git clone https://github.com/Mohammad-AlTmimi/University_Project.git
cd University_Project

2. Set Up Environment Variables
Create a .env file in the project root:
# FastAPI Settings
APP_HOST=0.0.0.0
APP_PORT=8000

# PostgreSQL Settings
POSTGRES_USER=your_postgres_user
POSTGRES_PASSWORD=your_postgres_password
POSTGRES_DB=your_database_name
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# MongoDB Local Settings
MONGO_HOST=mongo
MONGO_PORT=27017
MONGO_DB=your_mongo_db_name

# MongoDB Atlas Settings
MONGO_ATLAS_URI=mongodb+srv://<username>:<password>@cluster0.mongodb.net/<dbname>?retryWrites=true&w=majority

# AWS EC2 Settings
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1

Replace placeholders with actual credentials.
3. Install Dependencies
pip install -r requirements.txt

4. Build and Run with Docker
docker-compose up --build

Access the API at http://localhost:8000/docs for Swagger UI.
5. Deploy to AWS EC2

Launch an EC2 instance (e.g., Ubuntu 20.04).
Install Docker and Docker Compose.
Copy project files to EC2 using scp or Git.
Set up security groups for ports 8000 (FastAPI), 5432 (PostgreSQL), and 27017 (MongoDB, if local).
Run docker-compose up --build on EC2.
Access via http://<ec2-public-ip>:8000.


Folder Structure
University_Project/
├── app/                    # FastAPI application code
│   ├── __init__.py
│   ├── main.py             # FastAPI app entry point
│   ├── api/                # API routes
│   │   ├── __init__.py
│   │   ├── admin.py        # Admin routes (service toggling, charts, uploads)
│   │   ├── chat.py         # Chat routes (messages, chats)
│   │   ├── user.py         # User routes (auth, profile)
│   │   └── guest.py        # Guest routes (chat for non-authenticated users)
│   ├── schemas/            # Pydantic models
│   │   ├── __init__.py
│   │   ├── admin.py        # Admin-related schemas
│   │   ├── chat.py         # Chat-related schemas
│   │   ├── user.py         # User-related schemas
│   │   └── ai.py           # AI-related schemas
│   ├── models/             # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── admin.py        # Admin model
│   │   ├── user.py         # User and UserPortal models
│   │   └── chat.py         # Chat model
│   ├── controlers/         # Business logic
│   │   ├── __init__.py
│   │   ├── admin.py        # Admin logic (e.g., token creation, env updates)
│   │   ├── user.py         # User logic (e.g., signup, login)
│   │   ├── chat.py         # Chat logic (e.g., message handling)
│   │   └── ai.py           # AI logic (e.g., PDF processing, embeddings)
│   ├── middlewares/        # Authentication middleware
│   │   ├── __init__.py
│   │   ├── auth/
│   │   │   ├── adminauth.py # Admin authentication
│   │   │   └── userauth.py  # User authentication
│   ├── database/           # Database connections
│   │   ├── __init__.py
│   │   ├── postgres.py     # PostgreSQL setup
│   │   └── mongo.py        # MongoDB setup
│   ├── nodatabase/         # MongoDB async client
│   │   ├── __init__.py
│   │   └── nodatabase.py   # MongoDB async setup
│   ├── mongodbatlas/       # MongoDB Atlas setup
│   │   ├── __init__.py
│   │   └── mongodbatlas.py # Atlas-specific logic
│   ├── ml_models/          # Machine learning models
│   │   ├── __init__.py
│   │   └── sbertmodel.py   # SBERT for question classification
│   ├── embeddings/         # Embedding generation
│   │   ├── __init__.py
│   │   └── embeddings.py   # Embedding logic
│   └── photos/             # User profile photos
├── tests/                  # Unit and integration tests
│   ├── __init__.py
│   ├── test_admin.py
│   ├── test_chat.py
│   ├── test_user.py
│   └── test_guest.py
├── scripts/                # Automation scripts
│   ├── setup_db.sh
│   └── deploy_ec2.sh
├── docker/                 # Docker configurations
│   ├── fastapi/Dockerfile
│   ├── postgres/Dockerfile
│   └── mongo/Dockerfile
├── .env                    # Environment variables
├── docker-compose.yml      # Docker Compose config
├── requirements.txt        # Python dependencies
├── README.md               # This file
└── .gitignore              # Git ignore

Folder and File Details

app/api/: Defines API routes (admin.py, chat.py, user.py, guest.py).
app/schemas/: Pydantic models for request/response validation.
app/models/: SQLAlchemy models for PostgreSQL tables.
app/controlers/: Business logic for API endpoints.
app/middlewares/auth/: JWT-based authentication for users and admins.
app/database/: PostgreSQL connection setup.
app/nodatabase/: MongoDB async client setup.
app/mongodbatlas/: MongoDB Atlas connection and search index logic.
app/ml_models/: SBERT model for question classification.
app/embeddings/: Embedding generation for AI search.
app/photos/: Stores user profile photos.
tests/: Unit tests for API endpoints.
scripts/: Automation for database setup and EC2 deployment.
docker/: Dockerfiles for FastAPI, PostgreSQL, and MongoDB.


API Endpoints
Below is a detailed list of all API endpoints, grouped by module, with descriptions, request/response formats, and examples.
Admin Routes (/api/admin)
1. Toggle Service

Endpoint: POST /api/admin/services/{service_id}/toggle
Description: Starts or stops a service (e.g., BUILD_TABLE_QUESTION) by updating the .env file.
Authentication: Admin JWT token required.
Request Body:{
  "action": "start"
}


Response:{
  "message": "Service BUILD_TABLE_QUESTION started successfully",
  "Token": "jwt_token"
}


Example:curl -X POST "http://localhost:8000/api/admin/services/BUILD_TABLE_QUESTION/toggle" \
-H "Authorization: Bearer <admin_jwt_token>" \
-H "Content-Type: application/json" \
-d '{"action": "start"}'



2. Get Charts

Endpoint: GET /api/admin/charts
Description: Retrieves analytics, including total users and message type counts.
Authentication: Admin JWT token required.
Response:{
  "total_users": 100,
  "message_type_counts": {
    "general": 50,
    "build_chat": 30
  }
}


Example:curl -X GET "http://localhost:8000/api/admin/charts" \
-H "Authorization: Bearer <admin_jwt_token>"



3. Get Services

Endpoint: GET /api/admin/services
Description: Retrieves the status of allowed services.
Authentication: Admin JWT token required.
Response:{
  "SERVICE_BUILD_TABLE_QUESTION_ENABLED": "start"
}


Example:curl -X GET "http://localhost:8000/api/admin/services" \
-H "Authorization: Bearer <admin_jwt_token>"



4. Upload Semester Courses

Endpoint: POST /api/admin/uploadsemestercourses
Description: Uploads an Excel file (.xlsx) containing semester courses to MongoDB.
Authentication: Admin JWT token required.
Request: Form-data with file (Excel file).
Response:{
  "message": "File uploaded successfully",
  "inserted_id": "mongo_document_id",
  "Token": "jwt_token"
}


Example:curl -X POST "http://localhost:8000/api/admin/uploadsemestercourses" \
-H "Authorization: Bearer <admin_jwt_token>" \
-F "file=@/path/to/courses.xlsx"



5. Upload PDF

Endpoint: POST /api/admin/upload-pdf
Description: Uploads a PDF, extracts text, generates embeddings, and stores in MongoDB Atlas with search indexes.
Authentication: Admin JWT token required.
Request: Form-data with file (PDF file).
Response:{
  "message": "PDF processed and saved successfully.",
  "Token": "jwt_token"
}


Example:curl -X POST "http://localhost:8000/api/admin/upload-pdf" \
-H "Authorization: Bearer <admin_jwt_token>" \
-F "file=@/path/to/document.pdf"



6. Get Courses

Endpoint: GET /api/admin/courses
Description: Retrieves the latest semester courses from MongoDB.
Authentication: Admin JWT token required.
Response:{
  "Courses": {
    "_id": "mongo_document_id",
    "create_time": "2025-06-01T10:00:00",
    "courses": [
      {"course_id": "CS101", "name": "Intro to CS"},
      {"course_id": "CS102", "name": "Data Structures"}
    ]
  },
  "Token": "jwt_token"
}


Example:curl -X GET "http://localhost:8000/api/admin/courses" \
-H "Authorization: Bearer <admin_jwt_token>"



7. Get Students

Endpoint: GET /api/admin/students?start=1&end=10
Description: Retrieves a paginated list of students.
Authentication: Admin JWT token required.
Query Parameters:
start: Starting index (default: 1).
end: Ending index (default: 10).


Response:{
  "Students": [
    {"id": "user_id", "name": "John Doe", "portal_id": "12345"},
    {"id": "user_id2", "name": "Jane Doe", "portal_id": "12346"}
  ],
  "Token": "jwt_token"
}


Example:curl -X GET "http://localhost:8000/api/admin/students?start=1&end=10" \
-H "Authorization: Bearer <admin_jwt_token>"



Chat Routes (/api/chat)
1. Add Message

Endpoint: POST /api/chat/addmessage
Description: Sends a message in a chat (new or existing) and streams an AI response.
Authentication: User JWT token required.
Request Body:{
  "chat_id": "newchat",
  "message": "What is the course schedule?"
}


Response: Streaming response with AI-generated content.data: {"content": "The course schedule is..."}
data: {"status": "[DONE]", "chat_id": "chat_id", "Token": "jwt_token"}


Example:curl -X POST "http://localhost:8000/api/chat/addmessage" \
-H "Authorization: Bearer <user_jwt_token>" \
-H "Content-Type: application/json" \
-d '{"chat_id": "newchat", "message": "What is the course schedule?"}'



2. Get Chats

Endpoint: GET /api/chat/chats
Description: Retrieves a user’s chat history.
Authentication: User JWT token required.
Response:{
  "Chats": [
    {"id": "chat_id", "title": "Course Inquiry", "last_interaction": "2025-06-01T10:00:00"},
    {"id": "chat_id2", "title": "General Question", "last_interaction": "2025-06-01T09:00:00"}
  ],
  "Token": "jwt_token"
}


Example:curl -X GET "http://localhost:8000/api/chat/chats" \
-H "Authorization: Bearer <user_jwt_token>"



3. Get Messages

Endpoint: GET /api/chat/messages?chat_id=<chat_id>&start=1&end=10
Description: Retrieves paginated messages for a specific chat.
Authentication: User JWT token required.
Query Parameters:
chat_id: Chat ID.
start: Starting index (default: 1).
end: Ending index (default: 10).


Response:{
  "messages": [
    {"user_id": "user_id", "message": "Hello", "type": "general", "chat_id": "chat_id", "create_time": "2025-06-01T10:00:00"},
    {"user_id": "user_id", "message": "Hi there", "type": "response", "chat_id": "chat_id", "create_time": "2025-06-01T10:01:00"}
  ],
  "Token": "jwt_token"
}


Example:curl -X GET "http://localhost:8000/api/chat/messages?chat_id=chat_id&start=1&end=10" \
-H "Authorization: Bearer <user_jwt_token>"



User Routes (/api/user)
1. Signup

Endpoint: POST /api/user/signup
Description: Creates a new user with portal credentials.
Request Body:{
  "portal_id": "12345",
  "portal_password": "portal_pass",
  "password": "user_pass",
  "name": "John Doe"
}


Response:{
  "User": {"id": "user_id", "name": "John Doe", "portal_id": "12345"},
  "Token": "jwt_token",
  "Name": "John Doe"
}


Example:curl -X POST "http://localhost:8000/api/user/signup" \
-H "Content-Type: application/json" \
-d '{"portal_id": "12345", "portal_password": "portal_pass", "password": "user_pass", "name": "John Doe"}'



2. Login

Endpoint: POST /api/user/login
Description: Authenticates a user with portal ID and password.
Request Body:{
  "portal_id": "12345",
  "password": "user_pass"
}


Response:{
  "message": "Login successful",
  "user": {"id": "user_id", "name": "John Doe", "portal_id": "12345"}
}


Example:curl -X POST "http://localhost:8000/api/user/login" \
-H "Content-Type: application/json" \
-d '{"portal_id": "12345", "password": "user_pass"}'



3. Change Photo

Endpoint: POST /api/user/changephoto
Description: Uploads a user profile photo (JPEG/PNG).
Authentication: User JWT token required.
Request: Form-data with file (image file).
Response:{
  "message": "Photo Update Complete",
  "Token": "jwt_token"
}


Example:curl -X POST "http://localhost:8000/api/user/changephoto" \
-H "Authorization: Bearer <user_jwt_token>" \
-F "file=@/path/to/photo.jpg"



4. Get Photo

Endpoint: GET /api/user/photo
Description: Retrieves a user’s profile photo.
Authentication: User JWT token required.
Response: Image file (JPEG).
Example:curl -X GET "http://localhost:8000/api/user/photo" \
-H "Authorization: Bearer <user_jwt_token>" \
-o photo.jpg



5. Forget Password

Endpoint: POST /api/user/forgetpassword
Description: Initiates password reset by generating a token.
Request Body:{
  "portal_id": "12345",
  "portal_password": "portal_pass"
}


Response:{
  "token": "reset_token"
}


Example:curl -X POST "http://localhost:8000/api/user/forgetpassword" \
-H "Content-Type: application/json" \
-d '{"portal_id": "12345", "portal_password": "portal_pass"}'



6. Reset Password

Endpoint: POST /api/user/resetpassword
Description: Resets a user’s password using a reset token.
Request Body:{
  "password": "new_pass"
}


Request Header: Authorization: Bearer <reset_token>
Response:{
  "password": "new_pass"
}


Example:curl -X POST "http://localhost:8000/api/user/resetpassword" \
-H "Authorization: Bearer <reset_token>" \
-H "Content-Type: application/json" \
-d '{"password": "new_pass"}'



7. Change Password

Endpoint: POST /api/user/changepassword
Description: Changes a user’s password after verifying the old password.
Authentication: User JWT token required.
Request Body:{
  "old_password": "old_pass",
  "password": "new_pass"
}


Response:{
  "password": "new_pass"
}


Example:curl -X POST "http://localhost:8000/api/user/changepassword" \
-H "Authorization: Bearer <user_jwt_token>" \
-H "Content-Type: application/json" \
-d '{"old_password": "old_pass", "password": "new_pass"}'



8. Update Portal Password

Endpoint: POST /api/user/updateportalpassword
Description: Updates the user’s portal password.
Authentication: User JWT token required.
Request Body:{
  "password": "new_portal_pass"
}


Response:{
  "message": "Portal password updated successfully"
}


Example:curl -X POST "http://localhost:8000/api/user/updateportalpassword" \
-H "Authorization: Bearer <user_jwt_token>" \
-H "Content-Type: application/json" \
-d '{"password": "new_portal_pass"}'



Guest Routes (/api/guest)
1. Add Message

Endpoint: POST /api/guest/addmessage
Description: Allows guests to send messages and receive AI responses (no authentication required).
Request Body:{
  "chat_id": "Guest",
  "message": "What is the university address?"
}


Response: Streaming response with AI-generated content.data: {"content": "The university address is..."}
data: {"status": "[DONE]", "chat_id": "Guest"}


Example:curl -X POST "http://localhost:8000/api/guest/addmessage" \
-H "Content-Type: application/json" \
-d '{"chat_id": "Guest", "message": "What is the university address?"}'




Database Design
PostgreSQL

Users Table:
Columns: id (primary key), name, password_hash, role (enum: student, admin), updated (enum: Yes, No).


UserPortal Table:
Columns: id (primary key), portal_id (unique), portal_password, user_id (foreign key).


Chats Table:
Columns: id (primary key), user_id (foreign key), title, last_interaction, messages_number.



MongoDB (Local)

Messages Collection:
Documents: { "user_id": String, "message": String, "type": String, "chat_id": String, "create_time": Date, "template": String }.


Semester Courses Collection:
Documents: { "_id": ObjectId, "create_time": Date, "courses": Array, "Token": String }.



MongoDB Atlas

hu_information Collection:
Documents: Stores PDF chunks with embeddings for text/vector search.
Indexes: text_search (text index), vector_search (vector index).




Deployment Notes

AWS EC2: Use a t2.micro instance for testing or t2.medium for production. Configure security groups for ports 8000, 5432, and 27017 (if using local MongoDB).
MongoDB Atlas: Ensure the cluster allows EC2 IP access.
Security: Store credentials in .env or AWS Secrets Manager. Use HTTPS in production.
Scaling: Add an Application Load Balancer for high traffic.


Testing
Run tests with:
pytest tests/

Tests cover user authentication, chat functionality, admin operations, and guest messaging.

Contributing

Fork the repository.
Create a feature branch (git checkout -b feature/your-feature).
Commit changes (git commit -m "Add your feature").
Push to the branch (git push origin feature/your-feature).
Open a pull request.


Troubleshooting

API Not Responding: Check .env credentials and Docker container status.
Database Errors: Verify PostgreSQL/MongoDB connections and port mappings.
EC2 Issues: Ensure security groups allow required ports and AWS credentials are valid.


License
MIT License. See LICENSE file for details.

Acknowledgments

Hebron University for the project assignment.
FastAPI, Docker, and AWS communities for excellent tools and documentation.
MongoDB Atlas for cloud-hosted database services.

