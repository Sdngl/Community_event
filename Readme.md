# EventHub - Event Management System

EventHub is a robust, Flask-based web application designed to facilitate the creation, discovery, and management of community events. It provides a platform for organizers to publish events and for users to register and participate.

## Features

*   **User Authentication**: Secure registration and login system with role-based access control (User, Organizer, Admin).
*   **Event Management**: Organizers can create, update, and manage events.
*   **Event Discovery**: Browse upcoming events, filter by category [Coming Soon], and view details.
*   **Registration System**: Users can register for events, track their registrations, and view their history.
*   **Admin Dashboard**: comprehensive dashboard for administrators to manage users and events.
*   **Responsive Design**: Built with Bootstrap 5 for a seamless experience on all devices.

## Technology Stack

*   **Backend**: Python, Flask
*   **Database**: SQLite (SQLAlchemy ORM)
*   **Frontend**: HTML5, CSS3, Bootstrap 5, JavaScript
*   **Forms**: Flask-WTF
*   **Authentication**: Flask-Login

## Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/eventhub.git
    cd eventhub
    ```

2.  **Create a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment:**
    Create a `.env` file in the root directory (optional, defaults are provided in `config.py`):
    ```env
    SECRET_KEY=your-secret-key
    DATABASE_URL=sqlite:///site.db
    ```

5.  **Initialize the Database:**
    ```bash
    flask create-db
    flask seed-db  # Populates the database with sample data (Admin, Organizer, Events)
    ```

6.  **Run the Application:**
    ```bash
    flask run
    ```
    The application will be available at `http://localhost:5000`.

## User Roles & Credentials (Seed Data)

If you ran `flask seed-db`, the following accounts are available:

*   **Admin**: `admin` / `admin123`
*   **Organizer**: `organizer` / `organizer123`
*   **User**: `user` / `user123`

## Directory Structure

*   `app.py`: Application factory and entry point.
*   `models.py`: Database models.
*   `routes/`: Blueprint definitions for application logic.
*   `templates/`: HTML templates.
*   `static/`: CSS, JavaScript, and images.
*   `tests/`: Unit and integration tests.

## Contributing

1.  Fork the repository.
2.  Create a feature branch (`git checkout -b feature/AmazingFeature`).
3.  Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4.  Push to the branch (`git push origin feature/AmazingFeature`).
5.  Open a Pull Request.

## License

Distributed under the MIT License. See `LICENSE` for more information.
