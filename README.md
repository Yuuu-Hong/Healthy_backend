# Flask Fullstack App Backend

This is the backend part of the Flask Fullstack Application. It provides APIs for user registration, login, and data management.

## Project Structure

```
backend/
├── app.py                # Entry point of the backend application
├── models.py             # Data models for the application
├── routes/               # Contains route definitions
│   ├── __init__.py       # Initializes the routes
│   ├── auth.py           # User authentication routes (registration, login)
│   └── users.py          # User data management routes (CRUD operations)
├── database/             # Database files
│   └── db.sqlite3        # SQLite database file
├── requirements.txt      # Python dependencies
└── README.md             # Documentation for the backend
```

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd flask-fullstack-app/backend
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Running the Application

To run the backend application, execute the following command:
```
python app.py
```

The application will start on `http://127.0.0.1:5000`.

## API Endpoints

- **User Registration**: `POST /api/register`
- **User Login**: `POST /api/login`
- **Get Users**: `GET /api/users`
- **Create User**: `POST /api/users`
- **Update User**: `PUT /api/users/<id>`
- **Delete User**: `DELETE /api/users/<id>`

## Database

The application uses SQLite for data storage. The database file is located in the `database` directory.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.