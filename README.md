# Subman - Subscriptions Manager Project

## Description
Subsman is a web application that allows users to manage (CRUD) their service subscriptions (Netflix, Amazon Prime...) and offers the following features:
- Adding subscriptions containing:
    - Service name
    - Date of subscription start
    - Price
    - Recurrence of the payment 

## Technologies
- Python3
- Flask
- HTML/CSS
- Bootstrap
- SQLAlchemy
- SQLite

## Usage
1. Install python packages
    ```bash
    pip3 install -r requirements.txt
    ```
2. Create SQLite database: from the project folder run:
    ```bash
    sqlite3 subman.db
    .exit
    ```
3. Start the flask server:
    ```bash
    python3 application.py
    ```
4. Open browser and go to the address http://localhost:5000

## Screenshots
- Index page:
![](https://i.imgur.com/Mjnzub0.png)

- Login/Register:
![](https://i.imgur.com/BgsJQFn.png)
![](https://i.imgur.com/DaqBciL.png)

- Add subscription:
![](https://i.imgur.com/sXPdeWQ.png)

- Update/delete subscription:
![](https://i.imgur.com/4P66v66.png)
![](https://i.imgur.com/PmSKpSU.png)