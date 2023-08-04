import random


def map_ethnicity(code):
    ethnicity_mapping = {
        'black': '1',
        'latino': '2',
        'white': '3'
    }
    return ethnicity_mapping.get(code, 'Unknown')


def reverse_map_ethnicity(code):
    ethnicity_mapping = {
        '1': 'black',
        '2': 'latino',
        '3': 'white'
    }
    return ethnicity_mapping.get(code, 'Unknown')


def validate_session_id(session_id):
    if not session_id.isdigit() or len(session_id) != 4:
        return False
    return True


def get_race_digit(ethnicity):
    if ethnicity == 'random':
        return str(random.choice([1, 2, 3]))
    else:
        return str(map_ethnicity(ethnicity))
