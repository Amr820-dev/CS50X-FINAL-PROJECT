# YOUR PROJECT TITLE: Auto Market
#### Video Demo:  https://youtu.be/kQI30Ea0g2I
#### Description:

Overview:-

This project is a full web application built using Flask, SQLite, HTML, CSS, and JavaScript. It serves as a simple marketplace for new and used cars, allowing users to browse available vehicles, view full details, and submit purchase requests either in cash or through installment plans. The website is designed to be clean, user-friendly, and structured according to the principles taught throughout the CS50x course.
The application includes multiple routes, dynamic templates using Jinja, a structured database, form handling with validation, sessions, and secure user interactions. It aims to demonstrate my understanding of backend development, database usage, and full-stack application structuring. The project is fully functional and can be run locally using Flask.

Project Features:-

1.Home Page:-

The home page introduces the website and offers navigation to key sections such as new cars, used cars, services, and contact pages. It uses a base layout template and inherits shared design elements.

2.New Cars Section:-

This is the main feature of the project. Users can:

Browse available new cars

View car images

See details such as brand, year, price, mileage, and description

Navigate to the individual car details page using dynamic URLs

Each car is retrieved from the database using query_db and rendered through Jinja templates. Image fallback logic is included if no custom image is available.

3.New Car Details Page:-

When the user selects a car, they are taken to a detailed page that shows:

Car title

Brand and model year

Mileage

Price

Description

Image stored in /static/images/uploads/

A button to proceed with purchasing

This page displays all information dynamically based on the car_id in the URL.

4.Purchase Options:-

The buying process includes:

A "Buy Now" page showing the chosen car

Two buttons: Pay in Cash and Installment Plan

Dynamic routes containing the car ID, such as /new_cars/3/buy

Both options lead to different forms.

5.Pay in Cash Form

The "Buy in Cash" page includes:

Name, email, phone, and address fields

A POST request that stores the order in the database

Flash messages confirming success

Redirect to a thank-you page

The backend validates the input and inserts an order into the SQLite database with payment_type = "cash".

6.Installment Plan Form:-

This form includes:

User details (name, email, phone, address)

Down payment field

Installment period dropdown (12–48 months)

A POST request that stores installment-specific details in the database and redirects to a thank-you page

Example calculations are shown at the bottom of the page.

7.Database Structure

The project uses an SQLite database with tables such as:

cars Table

id

title

brand

year

km

price

image

description

created_at

orders Table

id

user_id

car_id

payment_type

details

created_at

Helper functions query_db() and execute_db() are used to interact with the database safely.

8.Templates Structure

The project uses Flask’s template inheritance:

layout.html → main structure

index.html

new_cars.html

new_car_details.html

application_buying_new_car.html

buy_cash.html

buy_installment.html

thank_you_new_car.html

CSS and JavaScript are stored in /static/css/ and /static/js/.


9.How to Run the Application:-

Step 1 — Install Requirements
pip install flask

Step 2 — Initialize the Database

Make sure cars.db is inside the project folder.

Step 3 — Run the App
python app.py


or

flask run

Step 4 — Open in Browser
http://127.0.0.1:5000/

10.Video Explanation:-

The project is accompanied by a video walkthrough as required by CS50x.
In the video, I explain:

What the project does

How each part of the app works

How the routes, templates, and database interact

How to run the application locally

Conclusion

This project represents everything I learned in CS50x — from Python and Flask to HTML, SQL, forms, sessions, state management, and template design. I built a complete web application that allows users to browse cars and submit purchase requests. The code demonstrates understanding of backend logic, dynamic rendering, data flow, and web development fundamentals.

This was a challenging but rewarding project, and I am proud of the final result.
