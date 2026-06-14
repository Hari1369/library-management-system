# Python Setup Guide for Running Scripts

# Method 1:
#   Step 1: Download Python :-
#       a)  Go to: https://www.python.org/downloads/
#       b)  Choose the version for your OS (Windows, Mac, Linux).
#       c)  Tip: For beginners, Python 3.x is recommended.
#   Step 2: Install Python :-
#       a)  Run the downloaded installer.
#       b)  Important: Check the box: Add Python to PATH.
#       c)  Click Install Now and follow the prompts.
#   Step 3: Verify Installation :-
#       a)  Open Command Prompt (Windows) or Terminal (Mac/Linux).
#       b)  Run:-
#               python --version or python3 --version
#       c)  You should see something like:
#               Python 3.x.x

# Method 2:
#   Step 1: Install Python :-
#       Follow Method 1 above if Python is not installed.
#   Step 2: Create a Project Folder
#       mkdir 'Question Sets' and cd 'Question Sets'
#           a) Run:-
#               python -m venv venv
#           or on Mac/Linux:
#               python3 -m venv venv
#   Step 4: Activate the Virtual Environment
#       a) Windows:
#           venv\Scripts\activate
#       b) Mac/Linux:
#           source venv/bin/activate
#   You’ll notice (venv) appears in your terminal prompt.
#   Step 6: Run Python Scripts
#       a)  Inside your project folder, create .py files (example: python_list.py).
#       b)  Run the script using:
#           python python_list.py or python3 python_list.py

#   Summary Comparison:-
#       a)  For simple learning scripts: Installing Python globally is fine.
#       b)  For organized project work: Using a virtual environment is better because it keeps dependencies isolated.


#   ====================================================================================================
#   | Method                   | Best For               | Requires Virtualenv? | Recommended?          |
#   | ------------------------ | ---------------------- | -------------------- | --------------------- |
#   | Official Python Download | Beginners, small tests | No                   | Good for quick start  |
#   | Virtual Environment      | Projects, Django apps  | Yes                  | Best for clean setups |
#   ====================================================================================================

# Method 3:
#   Cron Job Installation & Setup (Linux/Mac)
#   Step 1: Check if Cron is Installed :-
#       a) Run:-
#               crontab -l
#       b) If you see "no crontab for user", cron is installed.
#
#   Step 2: Install Cron (if not installed) :-
#       a) Ubuntu/Debian:
#               sudo apt update
#               sudo apt install cron
#
#       b) CentOS/RHEL:
#               sudo yum install cronie
#
#   Step 3: Start and Enable Cron Service :-
#       a) Ubuntu/Debian:
#               sudo systemctl start cron
#               sudo systemctl enable cron
#
#       b) CentOS/RHEL:
#               sudo systemctl start crond
#               sudo systemctl enable crond
#
#   Step 4: Create a Cron Job :-
#       a) Open cron editor:
#               crontab -e
#
#       b) Example: Run a Python script every day at 9 AM:
#               0 9 * * * /path/to/venv/bin/python /path/to/script.py
#
#   Step 5: Verify Cron Jobs :-
#       a) Run:
#               crontab -l
#
#   Summary:-
#       Cron jobs are used for scheduling automated tasks such as
#       sending emails, cleaning databases, running reports, etc.


# Method 4:
#   Celery & Redis Installation (Python Projects/Django)
#
#   Step 1: Install Redis Server :-
#       a) Ubuntu/Debian:
#               sudo apt update
#               sudo apt install redis-server

#   Step 2: Start Redis Service :-
#       a) Linux:
#               sudo systemctl start redis-server
#               sudo systemctl enable redis-server
#
#
#   Step 3: Verify Redis is Running :-
#       a) Run:
#               redis-cli ping
#
#       b) Expected Output:
#               PONG
#
#   Step 4: Activate Your Python Virtual Environment :-
#       a) Linux/Mac:
#               source venv/bin/activate
#
#   Step 5: Install Celery and Redis Python Packages :-
#       a) Run:
#               pip install celery redis
#
#   Step 6: Save Project Dependencies :-
#       a) Run:
#               pip freeze > requirements.txt
#
#   Step 7: Start Celery Worker :-
#       a) Django Example:
#               celery -A project_name worker --loglevel=info
#
#   Step 8: Start Celery Beat (Scheduled Tasks) :-
#       a) Run:
#               celery -A project_name beat --loglevel=info
#
#   Summary:-
#       Redis works as a message broker that stores task queues.
#       Celery processes background tasks like sending emails,
#       generating reports, notifications, and scheduled jobs.


#   ===========================================================================================================
#   | Method                   | Best For                       | Requires Setup? | Recommended?              |
#   | ------------------------ | ------------------------------ | ---------------- | ------------------------ |
#   | Cron Job                 | OS-level scheduled tasks       | Yes              | Good for simple scripts  |
#   | Celery + Redis           | Django background processing   | Yes              | Best for scalable apps   |
#   ===========================================================================================================