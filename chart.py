import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import io
import base64
from flask import render_template
from google_sheets import get_rt_data  # Assuming data.py is where get_rt_data is defined

def render_seaborn_chart(session_id):
	if session_id.method == 'POST':
		dimension = session_id.form['dimension']
		printf('session_id at render:', session_id)
	else:
		dimension = 'Anger'	
		
	# Load hume data from csv
	officer_df = pd.read_csv('datasets/OF_language.csv')
	driver_df = pd.read_csv('datasets/DF_language.csv')
	scene_df = pd.read_csv('datasets/O+D_F_language.csv')

	# Load reaction times data from the Google Spreadsheet
	df_rt = get_rt_data()
    # Filter df_rt to only include rows where the session_id matches the session_id passed to the function
	df_rt = df_rt.loc[df_rt['session_id'] == session_id]

	# Convert the 'session_ID' and 'ethnicity' columns to integer
	df_rt['session_id_int'] = df_rt['session_id'].astype(int)
	df_rt['ethnicity'] = df_rt['ethnicity'].astype(int)

	# Map the ethnicity numbers to their corresponding names
	ethnicity_mapping = {
		1: 'Black',
		2: 'Latino',
		3: 'White'
	}
	df_rt['ethnicity'] = df_rt['ethnicity'].map(ethnicity_mapping)

	# Filter the DataFrame to include only the desired ethnicity
	desired_ethnicity = 'Black'
	interventions_df = df_rt[df_rt['ethnicity'] == desired_ethnicity]

	plt.figure(figsize=(15, 5))

	plt.xlim(0, 180)  # Set x-axis limits to 0 and 180

	# Define a color palette with higher contrast
	color_palette = ["#6699CC", "#CC6666"]

	# Plot the Scene data
	scene_line = sns.lineplot(data=scene_df, x='BeginTime', y=dimension, color='green')

	# Plot the Officer data
	officer_line = sns.lineplot(data=officer_df, x='BeginTime', y=dimension, color=color_palette[0])

	# Plot the Driver data
	driver_line = sns.lineplot(data=driver_df, x='BeginTime', y=dimension, color=color_palette[1])

	# Interpolate the dimension value of the scene at the response times
	response_dimension = np.interp(interventions_df['reaction_t'], scene_df['BeginTime'], scene_df[dimension])

	# Add the scatter plot on top of the line plot
	colors = {desired_ethnicity: 'black'}
	scatter = plt.scatter(interventions_df['reaction_t'], response_dimension, c=interventions_df['ethnicity'].map(colors), s=10, zorder=10)

	# Create legend for the lines
	line_legend = [officer_line.lines[1], driver_line.lines[2]]

	# Create legend for the scatter plot
	scatter_legend = [plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='black', markersize=8)]

	# Combine the legends
	legend_handles = line_legend + scatter_legend
	legend_labels = ['Officer', 'Driver', 'Responses']

	# Add the combined legend to the plot
	plt.legend(handles=legend_handles, labels=legend_labels, loc='best', frameon=False, prop={'family':'Arial Narrow', 'size': 10})

	plt.title(f'Evolution of {dimension} Over Time', fontsize=20, fontname='Arial Narrow')
	plt.text(0.5, 0.95, f'POI ethnicity: {desired_ethnicity}', horizontalalignment='center', fontsize=11, transform=plt.gca().transAxes)
	plt.ylim(0, 1)# Set y-axis limits to 0 and 1

	# Set background color to white
	plt.gca().set_facecolor('white')

	# Set tick label font size and style
	plt.xticks(fontsize=12, fontname='Arial Narrow')
	plt.yticks(fontsize=12, fontname='Arial Narrow')

	# Set axis labels font size and style
	plt.xlabel('Time (s)', fontsize=10, fontname='Arial Narrow')
	plt.ylabel(f'{dimension} Level', fontsize=10, fontname='Arial Narrow')

	# Despine top and right axes
	sns.despine(top=True, right=True)

	# Save the figure to a BytesIO object
	bytes_image = io.BytesIO()
	plt.savefig(bytes_image, format='png')
	bytes_image.seek(0)

	# Convert the BytesIO object to a base64-encoded string
	base64_png = base64.b64encode(bytes_image.getvalue()).decode('ascii')

	# Pass the base64-encoded string to the template
	session_id = session_id.view_args['session_id']
	return render_template('analysis.html', chart_image=base64_png, session_id=session_id, ethnicity=desired_ethnicity)