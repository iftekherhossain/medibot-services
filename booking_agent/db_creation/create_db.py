import sqlite3
from datetime import datetime, timedelta
import random

# Connect to SQLite database
conn = sqlite3.connect('appointments.db')
cursor = conn.cursor()

# Create the updated appointments table with a single datetime column
cursor.execute('''
CREATE TABLE IF NOT EXISTS appointments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    status TEXT CHECK(status IN ('available', 'unavailable', 'booked')) DEFAULT 'available',
    name TEXT,
    personal_id TEXT
)
''')

# Create the users table if it does not exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    personal_id TEXT NOT NULL
)
''')

# Define the date range: next three months
today = datetime.now()
end_date = today + timedelta(days=90)

# Define available hours (8 AM to 6 PM)
available_hours = [f"{hour}:00" for hour in range(8, 19)]

# Generate appointments for the next three months
current_date = today
while current_date <= end_date:
    for hour in available_hours:
        # Randomly decide if the slot is booked or available, with more bookings than available slots
        status = 'booked' if random.random() < 0.75 else 'available'
        name = None
        personal_id = None
        if status == 'booked':
            name = f"User{random.randint(1, 100)}"
            personal_id = f"PID{random.randint(1000, 9999)}"
        
        # Combine date and time into a single datetime string
        datetime_combined = f"{current_date.strftime('%Y-%m-%d')} {hour}"
        
        # Insert the appointment into the database
        cursor.execute("INSERT INTO appointments (date, status, name, personal_id) VALUES (?, ?, ?, ?)",
                       (datetime_combined, status, name, personal_id))
    
    # Move to the next day
    current_date += timedelta(days=1)

# Commit the changes and close the connection
conn.commit()
conn.close()
