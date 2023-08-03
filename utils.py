def map_ethnicity(code):
	ethnicity_mapping = {
		'black': '1',
		'latino': '2',
		'white': '3'
	}
	return ethnicity_mapping.get(code, 'Unknown')


def validate_session_id(session_id):
	if not session_id.isdigit() or len(session_id) != 4:
		return False
	return True
