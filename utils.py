def map_ethnicity(code):
	ethnicity_mapping = {
		1: 'Black',
		2: 'Latino',
		3: 'White'
	}
	return ethnicity_mapping.get(code, 'Unknown')

def inverse_ethnicity_mapping(ethnicity):
	reverse_ethnicity_mapping = {
		'Black': '1',
		'Latino': '2',
		'White': '3'
	}
	return reverse_ethnicity_mapping.get(ethnicity, 'Unknown')

def validate_session_id(session_id):
	if not session_id.isdigit() or len(session_id) != 4:
		return False
	return True