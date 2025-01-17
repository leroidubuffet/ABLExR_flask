# TRAINxR

For anonimization purposes, all names and contents of the application  are anonymized, and the training videos have been removed or changed with examples.

The TRAINxR Trainer Application is a fully functional prototype of a web-based training tool that allows trainers to create and manage training sessions. Trainees can join these sessions, watch a training video, and submit feedback. The application is built using Flask and integrates with Google Sheets for data storage.

## Features

- Create new training sessions
- Add reaction times for each session
- Add feedback for each session
- View and analyze session data
- Generate visualizations for session data

## Lessons learned

OOP basics:
- Objects, classes, inheritance, methods, attributes, constructors, polymorphism, encapsulation, and abstraction.

Flask:
- Classes, inheritance, methods, order of methods, virtual functions, file organization, and secure credentials handling.

Python:
- Docstrings, exception handling, Flake8, and import order.

JavaScript:
- Basic syntax and concepts.

Data visualization and ETL:
- Matplotlib and Seaborn.

MySQL and MariaDB:
- Basic SQL queries, connecting to a database, and creating and managing tables.

Google Sheets:
- Using Google Sheets to store and manage data.

Other:
- Constants, functions in different files, and Git: conventional commits, branching.

## Developer notes

### Data visualization

The chart that is shown on /analysis depends on the data generated by [Hume](https://www.hume.ai). To get that data you need to provide hume with three separate audio files:

- Officer: file containing only the officer's speech
- Driver: file containing only the driver's speech
- Scene: file containing both the officer and the drivers scene

None of the files should include the *intro* and *outro* voiceover, but it is probably best to add a silence of the same lenght at the beginning and the end of each file for accuracy in the data visualization.

At the present time hume outputs three different files: burst, laguage and prosody. This application uses the language output.

Those datasets are stored in /datasets:

- `OF_language.csv`: officer data

This data is used to plot the blue line.

- `DF_language.csv`: driver data

This data is used to plot the red line.

- `O+D_F_language.csv`: scene data

This data is used to generate `mean_dimensions.csv`, a set of values that represent the means of the values of the driver and the officer for every dimension. To calculate the means use `means_calculator.py`.

The resulting file must be named `mean_dimensions.csv` and placed into /datasets. It will be used to plot an invisible line where the trainees responses (the black dots) are set.

## Instalation

- Clone the repo: `git clone https://github.com/leroidubuffet/TRAINxR_flask`
- Change into the directory: `cd TRAINxR_flask`
- Create a google sheets file to hold the application data
- Create a [Google Cloud](cloud.google.com) Project
- Create your own Google Cloud Service Account Authentication keys and save them into `credentials.json´ 
- Run the Flask app: `python app.py` or `flask --app app.py --debug run`

### Prerequisites

You will need to have the following tools installed on your machine:

- Python 3.6+
- Flask
- Flask-SocketIO
- gspread
- pandas
- numpy
- seaborn
- matplotlib

You can install the necessary python packages with pip:

`pip install flask flask-socketio gspread pandas numpy seaborn matplotlib`

### Usage

- Visit http://localhost:5000 in your web browser to view the app.
- Use the trainer dashboard to create new sessions and view session data.
- As a trainee, you can join a session, watch the training video, and submit feedback.
