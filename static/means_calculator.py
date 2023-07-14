import pandas as pd
import matplotlib.pyplot as plt


# Use this notebook to calculate the means between officer and driver

# Load the data
df1 = pd.read_csv('../datasets/OF_language.csv')
df2 = pd.read_csv('../datasets/DF_language.csv')

# Convert 'BeginTime' to a TimedeltaIndex
df1.index = pd.to_timedelta(df1['BeginTime'], unit='s')
df2.index = pd.to_timedelta(df2['BeginTime'], unit='s')

# Create a new dataframe that has a complete range of timestamps
complete_index = pd.timedelta_range(start=min(df1.index.min(), df2.index.min()), 
                                    end=max(df1.index.max(), df2.index.max()), freq='S')
df_complete = pd.DataFrame(index=complete_index)

# Concatenate the original dataframes to the new dataframe
df1 = pd.concat([df_complete, df1]).resample('1S').first().interpolate()
df2 = pd.concat([df_complete, df2]).resample('1S').first().interpolate()

# Merge the two DataFrames
df = pd.merge(df1, df2, left_index=True, right_index=True, suffixes=('_1', '_2'))

# Calculate the mean of the values from the two individuals
for column in df.columns:
    if column.endswith('_1'):
        df[column[:-2]] = df[[column, column[:-2] + '_2']].mean(axis=1)

# Drop the original columns
df = df.drop(columns=[column for column in df.columns if column.endswith('_1') or column.endswith('_2')])

# Now df contains the mean of the values from the two individuals for each second
df.to_csv('../datasets/mean_dimensions_new.csv', index=False)

plt.figure(figsize=(15, 6))

# Plot for df1
plt.plot(df1.index.total_seconds(), df1['Anxiety'], label='Person 1', color='blue')

# Plot for df2
plt.plot(df2.index.total_seconds(), df2['Anxiety'], label='Person 2', color='red')

# Plot for df (mean values)
plt.plot(df.index.total_seconds(), df['Anxiety'], label='Mean Values', color='green')

plt.title('Dimension Over Time')
plt.xlabel('Time (s)')
plt.ylabel('Dimension Value')
plt.legend()  # Display the legend
plt.show()