Internship Finder Website 🚀
Welcome to the Internship Finder Website repository! This project is a fully functional internship finder website built from scratch using Flask, HTML, CSS with Bootstrap, and MySQL.

MVC Architecture 🏗️
Model: Manages data storage and retrieval in the MySQL database.
View: Renders dynamic HTML templates using Jinja2.
Controller: Handles the flow of data between the model and view.

Authentication 🔒
User passwords are securely encrypted using the Werkzeug library, ensuring industry-standard hashing algorithms. Parameterized queries are utilized to prevent SQL injection. Sessions are created upon user sign-in and cleared upon logout, maintaining data privacy.

User Experience 👥
There are two types of users: Companies and Students. Upon registration and sign-in, users are redirected to their profile pages, where they can view and edit personal information.

Companies 🏢
Company profile pages allow for the insertion, editing, and deletion of internships. Student internship requests are displayed on the "Requests" page, along with their email and CV.

Students 👩‍🎓
Student profile pages enable the insertion or update of subject marks, with average and GPA calculated using the NumPy library. Students can apply for internships listed by companies on the internships page, but applications cannot be revised once submitted.

Just visit my linkedin if you want to see what it looks like. 