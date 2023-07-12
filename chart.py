import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import io
import base64
from flask import render_template
from google_sheets import get_rt_data_for_session
from constants import ETHNICITY_MAPPING, COLOR_PALETTE

def load_data(session_id):
	# Load hume data from csv
	df_officer = pd.read_csv('datasets/OF_language.csv')
	df_driver = pd.read_csv('datasets/DF_language.csv')
	df_scene = pd.read_csv('datasets/O+D_F_language.csv')

	# Load reaction times data from the Google Spreadsheet
	df_rt = get_rt_data_for_session(session_id)

	# Extract the ethnicity from the df_rt DataFrame
	ethnicity = df_rt['ethnicity'].iloc[0] if not df_rt.empty else 'Unknown'

	return df_officer, df_driver, df_scene, df_rt, ethnicity

def chart_render_seaborn_chart(session_id, dimension):
	df_officer, df_driver, df_scene, df_rt, ethnicity = load_data(session_id)

	plt.figure(figsize=(15, 5))

	plt.xlim(0, 180)  # Set x-axis limits to 0 and 180

	# Plot the Scene data
	scene_line = sns.lineplot(data=df_scene, x='BeginTime', y=dimension, color='green')

	# Plot the Officer data
	officer_line = sns.lineplot(data=df_officer, x='BeginTime', y=dimension, color=COLOR_PALETTE[0])

	# Plot the Driver data
	driver_line = sns.lineplot(data=df_driver, x='BeginTime', y=dimension, color=COLOR_PALETTE[1])

	# Interpolate the dimension value of the scene at the response times
	print(df_rt['reaction_t'].dtypes)
	print(df_rt['reaction_t'].unique())
	print(df_scene['BeginTime'].dtypes)
	print(df_scene['BeginTime'].unique())
	df_rt['reaction_t'] = pd.to_numeric(df_rt['reaction_t'], errors='coerce')

	response_dimension = np.interp(df_rt['reaction_t'], df_scene['BeginTime'], df_scene[dimension])

	# Add the scatter plot on top of the line plot
	scatter = plt.scatter(df_rt['reaction_t'], response_dimension, c='black', s=10, zorder=10)

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
	plt.ylim(0, 1)  # Set y-axis limits to 0 and 1

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
	return render_template('analysis.html', chart_image=base64_png, session_id=session_id, ethnicity=ethnicity)
