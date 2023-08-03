# Google sheets authentication
CREDENTIALS_FILE = 'credentials.json'
DOCUMENT_NAME = 'ABLExR-DATA'

# Ethnicities
ETHNICITY_MAPPING = {
    1: 'Black',
    2: 'Latino',
    3: 'White'
}

ETHNICITIES = ['random', 'black', 'latino', 'white']

# Officer, Driver, Scene dots
COLOR_PALETTE = ["#6497b1", "#ff6f69", "#011f4b"]

# Error messages
INVALID_PASSWORD = 'Invalid password. Please try again.'
SESSION_ID_EXISTS = 'Session ID already exists. Please try a different ID.'
SESSION_ID_NOT_EXIST = (
    'Session ID does not exist. Please try a different ID.'
)
SESSION_ID_MUST_BE_DIGIT = 'Session ID must be a 3 digit number.'
INSERT_FOUR_DIGIT_NUMBER = 'Insert a 4 digit number please.'

# File paths
OFFICER_F = 'datasets/OF_language.csv'
DRIVER_F = 'datasets/DF_language.csv'
SCENE_F = 'datasets/mean_dimensions.csv'
