# Equipment Request Management System

This project is an Equipment Request Management System built using Django. It allows users to view, request, and return equipment, while also managing user authentication and profiles. The system includes a dashboard to manage available equipment and user-specific profiles to track requested equipment.

## Features

- **User Authentication:**
  - Register an account.
  - Login and logout functionality.
  - User-specific equipment request tracking.

- **Equipment Management:**
  - View available equipment in store.
  - Request equipment (changes status to "In Field").
  - Return equipment (changes status to "In Store").

- **User Dashboard:**
  - Displays all available equipment and the user's requested equipment.
  
## Requirements

- Python 3.8+
- Django 3.2+
- Bootstrap 5 (for styling)
  
## Data



```bash
git clone https://github.com/wole-abraham/Django-Inventory.git
pip3 install django
pip3 install pillow
cd Django-Inventory
cd survery_system
-- You can create a admin account using
python3 manage.py createsuperuser / follow the prompt
python3 manage.py runserver

```
## Navigation
127.0.0.1:8000/create-user  -- to create an account
login with the username(case sensitive ) and password


![image](https://github.com/user-attachments/assets/fff12d83-6919-4bbe-b445-6bec9283422d)

![image](https://github.com/user-attachments/assets/07433cac-7a1a-43cd-a836-354f488388d4)

![image](https://github.com/user-attachments/assets/1014ed9d-d9f1-424c-aedc-c64885ccca45)

