# 🎉 Event Garden 🎉

Welcome to **Event Garden**, a 🌐 web-based event management system built using 🐍 Flask and SQLAlchemy with 🛢️ MySQL integration. This system empowers 👥 users to ✨ create, manage, and 📖 book events effortlessly while providing robust 🔧 administrative controls.

---

## 🛠️ Key Features

### 👥 User Features
- **👤 User Registration:**
  - Fields include 🖊️ username, 🔒 password, 🔁 confirm password, 📞 mobile number, 🎂 date of birth, ✉️ email ID, 🏙️ city, and 🗺️ state.
  - Ensures ✅ comprehensive field validation.
- **🔐 Secure Login:**
  - Access your account using ✉️ email and 🔒 password.
- **📄 User Pages:**
  - 🏠 Home
  - ℹ️ About
  - 🎟️ Events
  - 📝 Register Event
  - 🖼️ Gallery
  - 📞 Contact
  - 🔔 Notification

### 👩‍💼 Admin Features
- **🔧 Admin Dashboard:**
  - Exclusive access for 🧑‍💼 admin users.
  - Oversee all 👥 user activities.
- **🎟️ Event Management:**
  - ➕ Create, ✏️ update, ❌ delete, and 👀 view events.
  - Manage 📍 event locations, 💰 pricing, and 📊 capacities.
    
- **📊 User Monitoring:**
  - View 📋 lists of event creators and 🎟️ ticket bookers in a clear 🧮 tabular format.

### 🎟️ Event Details
- **📋 Comprehensive Fields:**
  - Includes 🏫 college name, 🏠 address, 📝 event details, 📍 location, 🕒 start and end times, ✍️ description, 🏷️ type, and 💰 price.
  - Prevents 🚫 scheduling conflicts for events at the same 📍 location and 🕒 time.
- **🏢 Hall Selection:**
  - Automatically populates 🏠 address, 🏷️ type, and 💰 price based on the chosen 🏢 hall.

### 🎟️ Ticket Booking
- Users can ✨ create and 📝 register for events by 🎟️ booking tickets conveniently.

---

## 🛠️ Installation Guide

### ⚙️ Prerequisites
- 🐍 Python 3.x
- 🛢️ MySQL Server
- 📦 Virtual environment (optional but recommended)

### 📜 Steps to Set Up
1. 🌀 Clone the repository:
   ```bash
   git clone https://github.com/PiyushRaj714/Event-Management-System
   ```

2. 🗂️ Navigate to the project directory:
   ```bash
   cd Event-Management-System
   ```

3. Set up a 📦 virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate # On 🪟 Windows: venv\Scripts\activate
   ```

4. 📥 Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Configure the 🛢️ database:
   - Create a MySQL 🛢️ database.
   - Update the `config.py` file with your 🛡️ database credentials.

6. Run 🗄️ database migrations:
   ```bash
   flask db upgrade
   ```

7. Start the 🖥️ development server:
   ```bash
   flask run
   ```

8. Access the 🖥️ application in your 🌐 browser:
   - Development: `http://127.0.0.1:5000`

---

## 🤝 Contributing
Contributions are welcome! 🌀 Fork the repository and create a 📨 pull request to propose any features or 🐞 bug fixes.

---

## 📜 License
This project is licensed under the ⚖️ MIT License. Refer to the `LICENSE` file for more details.


---
