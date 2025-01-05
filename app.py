from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import mysql.connector
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mail import Mail, Message
from datetime import datetime

app = Flask(__name__)

app.secret_key = 'your_secret_key'  # Set a secret key for session management


# Function to connect to the database
def get_db_connection():
    connection = mysql.connector.connect(
        host='localhost',
        database='event_project',
        user='user',
        password='pass'
    )
    return connection


# Configure Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'email'
app.config['MAIL_PASSWORD'] = 'password'
app.config['MAIL_DEFAULT_SENDER'] = 'email'

mail = Mail(app)


# Route for the signup page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':

        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role', 'user')
        email = request.form.get('email')


        if not username or not password or not email:
            return "All fields are required!", 400

        # Connect to the database and insert data
        connection = get_db_connection()
        cursor = connection.cursor()

        try:
            # Insert username, password, role, and email into the database
            cursor.execute(
                "INSERT INTO users (username, password, role, email) VALUES (%s, %s, %s, %s)",
                (username, password, role, email)
            )
            connection.commit()
            print(f"User {username} signed up successfully!")
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            connection.rollback()
        finally:
            cursor.close()
            connection.close()

        return redirect(url_for('login'))  # Redirect to login page after signup

    return render_template('signup.html')


# Route for the login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()

        cursor.close()
        connection.close()

        if user:
            role = user[3]  # Assuming role is the fourth column in the 'users' table

            # Store the username and role in the session
            session['username'] = username
            session['role'] = role

            if role == 'admin':
                return redirect(url_for('dashboard'))
            else:
                return redirect(url_for('user_dashboard'))

        else:
            return "Invalid credentials!"

    return render_template('login.html')


# Route for the home page for regular users
@app.route('/home')
def home():
    # Check if the user is logged in
    if 'username' in session:
        try:
            # Connect to the database
            connection = get_db_connection()
            cursor = connection.cursor()

            # Fetch events
            cursor.execute("SELECT name, date, venue FROM events")
            events = cursor.fetchall()

            # Fetch notifications for the logged-in user
            cursor.execute("SELECT message, timestamp FROM notifications WHERE receiver = %s ORDER BY timestamp DESC",
                           (session['username'],))
            notifications = cursor.fetchall()

            cursor.close()
            connection.close()

            # Render home page with events and notifications passed to the template
            return render_template('home.html', username=session['username'], events=events,
                                   notifications=notifications)
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            flash("An error occurred while fetching data. Please try again later.", "error")
            return render_template('home.html', username=session['username'], events=[], notifications=[])
    else:
        # Redirect to login page if user is not logged in
        return redirect(url_for('login'))


# Route for registering for an event
@app.route('/register_event/<int:event_id>', methods=['GET', 'POST'])
def register_event(event_id):
    # Connect to the database to fetch event details
    connection = get_db_connection()
    cursor = connection.cursor()

    # Get event details by ID (assuming event_id exists in the database)
    cursor.execute("SELECT name, date, venue, price FROM events WHERE id = %s", (event_id,))
    event = cursor.fetchone()

    if not event:
        return "Event not found!"

    if request.method == 'POST':
        # Get the number of tickets and payment details
        tickets = request.form['tickets']
        payment_method = request.form['payment_method']

        # Assuming the price is in the fourth column of the event
        total_amount = event[3] * int(tickets)

        # Store the registration (This would require a registration table in the database)
        cursor.execute(
            "INSERT INTO registrations (event_id, username, tickets, total_amount, payment_method) VALUES (%s, %s, %s, %s, %s)",
            (event_id, session['username'], tickets, total_amount, payment_method))
        connection.commit()

        # Redirect to confirmation page or homepage after successful registration
        return redirect(url_for('home'))

    cursor.close()
    connection.close()

    return render_template('register_event.html', event=event)


# Route for booking event
@app.route('/book_event/<int:event_id>', methods=['GET', 'POST'])
def book_event(event_id):
    # Fetch the event details based on event_id
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM events WHERE id = %s", (event_id,))
    event = cursor.fetchone()
    cursor.close()
    connection.close()

    if not event:
        return "Event not found!", 404

    if request.method == 'POST':
        # Get user input (number of tickets, payment method)
        tickets = int(request.form['tickets'])
        total_amount = event['price'] * tickets  # Assuming 'price' is fetched from the event
        payment_method = request.form['payment_method']  # e.g., 'Credit Card', 'PayPal'

        # Save registration to the database
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO registrations (event_id, username, tickets, total_amount, payment_method) VALUES (%s, %s, %s, %s, %s)",
            (event_id, session['username'], tickets, total_amount, payment_method))
        connection.commit()
        cursor.close()
        connection.close()

        # Redirect to a confirmation page after booking
        return redirect(url_for('booking_confirmation', event_id=event_id))

    return render_template('book_event.html', event=event)


@app.route('/booking_confirmation/<int:event_id>')
def booking_confirmation(event_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM registrations WHERE event_id = %s AND username = %s", (event_id, session['username']))
    registration = cursor.fetchone()
    cursor.close()
    connection.close()

    if not registration:
        return "Booking not found!", 404

    return render_template('booking_confirmation.html', registration=registration)


@app.route('/admin_dashboard')
def admin_dashboard():
    if 'username' in session and session['role'] == 'admin':
        connection = get_db_connection()
        cursor = connection.cursor()

        # Query to get registered events along with event details
        cursor.execute("""
             SELECT r.id, r.username, r.tickets, r.total_amount, r.payment_method, u.email, e.name, e.date, e.venue
    FROM registrations r
    JOIN users u ON r.id = u.id
    JOIN events e ON r.event_id = e.id
        """)
        registrations = cursor.fetchall()

        cursor.close()
        connection.close()

        return render_template('admin_dashboard.html', registrations=registrations)
    else:
        return redirect(url_for('login'))


@app.route('/add_event', methods=['GET', 'POST'])
def add_event():
    if 'username' in session and session['role'] == 'admin':
        if request.method == 'POST':
            # Get data from the form
            name = request.form['name']
            date = request.form['date']
            venue = request.form['venue']
            price = request.form['price']

            # Insert the new event into the database
            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO events (name, date, venue, price)
                VALUES (%s, %s, %s, %s)
            """, (name, date, venue, price))
            connection.commit()

            cursor.close()
            connection.close()

            return redirect(url_for('admin_dashboard'))  # Redirect back to the admin dashboard

        return render_template('add_event.html')
    else:
        return redirect(url_for('login'))

@app.route('/remove_event/<int:event_id>', methods=['GET', 'POST'])
def remove_event(event_id):
    if 'username' in session and session['role'] == 'admin':
        # Fetch the event to confirm deletion
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM events WHERE id = %s", (event_id,))
        event = cursor.fetchone()

        if event:  # Check if the event exists
            if request.method == 'POST':
                # Delete the event from the database
                cursor.execute("DELETE FROM events WHERE id = %s", (event_id,))
                connection.commit()
                flash('Event removed successfully!', 'success')
                return redirect(url_for('admin_dashboard'))  # Redirect back to the admin dashboard

            return render_template('remove_event.html', event=event)  # Render confirmation page
        else:
            flash('Event not found.', 'warning')
            return redirect(url_for('admin_dashboard'))  # Redirect if event doesn't exist

        cursor.close()
        connection.close()
    else:
        flash('You must be logged in as an admin to access this page.', 'warning')
        return redirect(url_for('login'))  # Redirect to login if not logged in as admin



@app.route('/logout')
def logout():
    # Remove the user from the session
    session.pop('username', None)
    session.pop('role', None)
    return redirect(url_for('login'))


@app.route('/send_email', methods=['GET', 'POST'])
def send_email():
    if request.method == 'POST':
        user_email = request.form['user_email']
        subject = request.form['subject']
        body = request.form['body']
        send_date = request.form['send_date']
        send_time = request.form['send_time']

        send_datetime_str = f"{send_date} {send_time}"
        send_datetime = datetime.strptime(send_datetime_str, "%Y-%m-%d %H:%M")

        formatted_datetime = send_datetime.strftime("%A, %B %d, %Y at %I:%M %p")

        body_with_datetime = f"{body}\n\nAppointment is scheduled to discuss further in person on: {formatted_datetime}"

        msg = Message(subject=subject,
                      recipients=[user_email],
                      body=body_with_datetime)

        try:
            mail.send(msg)
            flash('Email sent successfully!', 'success')
        except Exception as e:
            flash(f'Error sending email: {str(e)}', 'danger')

        return redirect(url_for('admin_dashboard'))

    return render_template('set_appointment.html')


@app.route('/set_appointment')
def set_appointment():
    # Retrieve the email from the URL query parameter
    user_email = request.args.get('email')
    return render_template('set_appointment.html', user_email=user_email)


@app.route('/send_notification/<receiver_username>', methods=['GET', 'POST'])
def send_notification(receiver_username):
    # Validate session and role
    if 'username' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))

    sender = session.get('username')  # The logged-in admin's username
    if request.method == 'POST':
        message = request.form['message']  # Notification message from the form

        # Connect to the database
        conn = get_db_connection()
        cursor = conn.cursor()

        # Insert notification into the database
        cursor.execute("""
            INSERT INTO notifications (sender, receiver, message, timestamp)
            VALUES (%s, %s, %s, NOW())
        """, (sender, receiver_username, message))
        conn.commit()  # Commit the transaction
        cursor.close()
        conn.close()  # Close the connection

        flash('Notification sent successfully!', 'success')
        return redirect(url_for('admin_dashboard'))  # Redirect back to the admin dashboard

    # Render the form for sending the notification
    return render_template('send_notification.html', receiver_username=receiver_username)


@app.route('/user_dashboard')
def user_dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch notifications for the logged-in user
    cursor.execute("SELECT sender, message, timestamp FROM notifications WHERE receiver = %s ORDER BY timestamp DESC", (username,))
    notifications = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('user_dashboard.html', notifications=notifications)


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


@app.route('/view_registered_events')
def view_registered_events():
    # Assuming the user's username is stored in the session after login
    username = session.get('username')

    if not username:
        return redirect(url_for('login'))  # If no username is in session, redirect to login page

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Query to get the user's registered events
        cursor.execute('''
            SELECT e.id, e.name, e.date, e.venue, e.price
            FROM events e
            JOIN registrations r ON e.id = r.event_id
            WHERE r.username = %s
        ''', (username,))  # Note the use of %s instead of ?

        registered_events = cursor.fetchall()

        # Make sure to close the cursor and connection
        cursor.close()
        conn.close()

        return render_template('viewEvent.html', events=registered_events)

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return render_template('error.html', error="Database error occurred.")

@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/search')
def search():
    query = request.args.get('q')
    # Process the search query here
    return f"Search results for: {query}"


@app.route("/", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        message = request.form["message"]

        # Create the email content
        msg = Message(
            subject="New Contact Us Message",
            recipients=["email"],  # The recipient's email address
            body=f"Name: {name}\nEmail: {email}\nMessage: {message}"
        )

        try:
            mail.send(msg)
            return render_template("index.html")
        except Exception as e:
            return f"Error: {e}"

    return render_template("index.html")


@app.route('/venues')
def list_venues():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM venues")
    venues = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('list_venues.html', venues=venues)


@app.route('/book_venue/<int:venue_id>', methods=['GET', 'POST'])
def book_venue(venue_id):
    if request.method == 'POST':
        user_id = session.get('user_id')
        booking_date = request.form['booking_date']
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        comments = request.form.get('comments')
        user_email = request.form['user_email']

        # Sending an email to the admin
        msg = Message(
            subject="New Venue Booking Request",
            recipients=["email"],
            body=f"""
            You have a new venue booking request from {user_email}.

            Booking Date: {booking_date}
            Start Time: {start_time}
            End Time: {end_time}
            Comments: {comments}
            """
        )

        try:
            mail.send(msg)
            return redirect(url_for('success'))  # Assuming you have a success page or route
        except Exception as e:
            return f"Error: {e}"

    return render_template('book_venue.html', venue_id=venue_id)


@app.route('/success')
def success():
    return "Booking confirmed! An email has been sent to the admin."

@app.route('/admin/bookings')
def admin_view_bookings():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))  # Ensure only admin can access

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT b.id, u.username, v.name AS venue_name, b.booking_date, b.start_time, b.end_time, b.status
        FROM bookings b
        JOIN users u ON b.user_id = u.id
        JOIN venues v ON b.venue_id = v.id
    """)
    bookings = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('admin_view_bookings.html', bookings=bookings)


@app.route('/add_venue', methods=['GET', 'POST'])
def add_venue():
    if 'username' in session and session['role'] == 'admin':
        if request.method == 'POST':
            name = request.form.get('name')
            location = request.form.get('location')
            capacity = request.form.get('capacity')
            description = request.form.get('description')

            if not name or not location or not capacity:
                flash("All fields are required.", 'error')
                return render_template('add_venue.html')

            try:
                capacity = int(capacity)
            except ValueError:
                flash("Capacity must be a number.", 'error')
                return render_template('add_venue.html')

            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute("SELECT id FROM users WHERE username = %s", (session['username'],))
            user_id = cursor.fetchone()[0]

            cursor.execute("""
                INSERT INTO venues (name, location, capacity, description, created_by)
                VALUES (%s, %s, %s, %s, %s)
            """, (name, location, capacity, description, user_id))

            connection.commit()
            cursor.close()
            connection.close()

            flash("Venue added successfully.", 'success')
            return redirect(url_for('admin_dashboard'))

        return render_template('add_venue.html')

    else:
        flash("You need to be logged in as admin to access this page.", 'error')
        return redirect(url_for('login'))


@app.route('/book_meeting', methods=['POST'])
def book_meeting():
    if request.method == 'POST':
        # Capture form data
        name = request.form['name']
        email = request.form['email']
        meeting_date = request.form['meeting_date']
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        comments = request.form.get('comments')

        # Create the email message
        msg = Message(
            subject="New Meeting Request",
            recipients=["nnm22cs007@nmamit.in.com"],
            body=f"""
            You have a new meeting request from {name} ({email}).

            Meeting Date: {meeting_date}
            Start Time: {start_time}
            End Time: {end_time}
            Comments: {comments}
            """
        )

        try:
            # Send the email
            mail.send(msg)

            # Redirect to user dashboard after email is sent successfully
            return redirect(url_for('user_dashboard'))

        except Exception as e:
            return f"Error: {e}"


if __name__ == '__main__':
    app.run(debug=True)
