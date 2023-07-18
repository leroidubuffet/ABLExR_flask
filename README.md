# ABLExR

The ABLExR Trainer Application is fully functional prototype of a web-based training tool that allows trainers to create and manage training sessions. Trainees can join these sessions, watch a training video, and submit feedback. The application is built using Flask and integrates with Google Sheets for data storage.

## Features

- Create new training sessions
- Add reaction times for each session
- Add feedback for each session
- View and analyze session data
- Generate visualizations for session data

## Developer notes

### Data visualization

The chart that is shown on /analysis depends on the data generated at [Hume](https://www.hume.ai). To get that data you need to provide hume with three separate audio files:

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

### Videos

- Scene 3: linked at templates/video.html

This file is a video rendering of the AV/AR scene 3 experience. 

- Hume: linked at templates/analysis.html

This file is a screencast of hume.ai showing the evolution of the language dimensions when playing the uploaded file.

## Instalation

- Clone the repo: `git clone https://github.com/miguelespada/ABLExR-microserver`
- Change into the directory: `cd ABLExR-Trainer`
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

## TODOs

- Update scene 3 video
- Update language datasets with hume and means dataset
- Update hume video
- Remove video controls in scene 3
- Implement credentials and secrets
- Generate and implement function classes
- Add a visual layer to the application
