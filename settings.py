import os

SESSION_CONFIGS = [
	dict(
		id='BR', # default DuckSoup namespace, should be changed per session
		name='brainstorm',
		display_name='Brainstorm',
		app_sequence=['brainstorm'],
		num_demo_participants=4,
		num_participants_allowed=[4, 6, 8, 10, 12, 14],
		locale="en",
		doc="There must be an even number of participants between 4 and 12. Available locales are 'en' and 'fr'."
	),
	dict(
		id='BR_DS', # default DuckSoup namespace, should be changed per session
		name='brainstorm_detect_silence',
		display_name='Brainstorm detect silence',
		app_sequence=['brainstorm_detect_silence'],
		num_demo_participants=8,
		num_participants_allowed=[4, 6, 8, 10, 12, 14],
		locale="en",
		doc="There must be an even number of participants between 4 and 12. Available locales are 'en' and 'fr'."
	),
	dict(
		id='BR_RS', # default DuckSoup namespace, should be changed per session
		name='brainstorm_rand_scripted',
		display_name='Brainstorm random scripted',
		app_sequence=['brainstorm_rand_scripted'],
		num_demo_participants=8,
		num_participants_allowed=[4, 6, 8, 10, 12, 14],
		locale="en",
		doc="There must be an even number of participants between 4 and 12. Available locales are 'en' and 'fr'."
	),
	dict(
		id='BR_IN', # default DuckSoup namespace, should be changed per session
		name='brainstorm_intel_av',
		display_name='Brainstorm intelligibility audio',
		app_sequence=['brainstorm_intel_av'],
		num_demo_participants=8,
		num_participants_allowed=[4, 6, 8, 10, 12, 14],
		locale="en",
		doc="There must be an even number of participants between 4 and 12. Available locales are 'en' and 'fr'."
	),	
	dict(
		id='BR_SM1', # default DuckSoup namespace, should be changed per session
		name='brainstorm_smile_audio',
		display_name='Brainstorm smile audio',
		app_sequence=['brainstorm_smile_audio'],
		num_demo_participants=8,
		num_participants_allowed=[4, 6, 8, 10, 12, 14],
		locale="en",
		doc="There must be an even number of participants between 4 and 12. Available locales are 'en' and 'fr'."
	),
	dict(
		id='BR_SM2', # default DuckSoup namespace, should be changed per session
		name='brainstorm_smile_video',
		display_name='Brainstorm smile video',
		app_sequence=['brainstorm_smile_video'],
		num_demo_participants=8,
		num_participants_allowed=[4, 6, 8, 10, 12, 14],
		locale="en",
		doc="There must be an even number of participants between 4 and 12. Available locales are 'en' and 'fr'."
	),		
	dict(
		id='BR_SM3', # default DuckSoup namespace, should be changed per session
		name='brainstorm_smile_av',
		display_name='Brainstorm smile audio video',
		app_sequence=['brainstorm_smile_av'],
		num_demo_participants=8,
		num_participants_allowed=[4, 6, 8, 10, 12, 14],
		locale="en",
		doc="There must be an even number of participants between 4 and 12. Available locales are 'en' and 'fr'."
	),	
	dict(
		id='BR_SM4', # default DuckSoup namespace, should be changed per session
		name='brainstorm_prolific_smile_video',
		display_name='Brainstorm prolific smile video',
		app_sequence=['brainstorm_prolific_smile_video'],
		num_demo_participants=8,
		num_participants_allowed=[4, 6, 8, 10, 12, 14],
		locale="en",
		doc="There must be an even number of participants between 4 and 12. Available locales are 'en' and 'fr'."
	),
	dict(
			id='BR_SM5', # default DuckSoup namespace, should be changed per session
			name='brainstorm_force_congruence',
			display_name='Brainstorm force congruence',
			app_sequence=['brainstorm_force_congruence'],
			num_demo_participants=8,
			num_participants_allowed=[4, 6, 8, 10, 12, 14],
			locale="en",
			doc="There must be an even number of participants between 4 and 12. Available locales are 'en' and 'fr'."
		),
	dict(
			id='BR_SM6', # default DuckSoup namespace, should be changed per session
			name='brainstorm_rand_scripted_face_syntax',
			display_name='Brainstorm random scripted face_syntax',
			app_sequence=['brainstorm_rand_scripted_face_syntax'],
			num_demo_participants=8,
			num_participants_allowed=[4, 6, 8, 10, 12, 14],
			locale="en",
			doc="There must be an even number of participants between 4 and 12. Available locales are 'en' and 'fr'."
		),	
	dict(
		id='CH', # default DuckSoup namespace, should be changed per session
		name='chatroulette',
		display_name='Chatroulette',
		app_sequence=['chatroulette'],
		num_demo_participants=4,
		num_participants_allowed=[2, 4, 6, 8, 10, 12, 14],
		doc="There must be an even number of participants between 2 and 8."
	),
	dict(
		id='DA_EN', # default DuckSoup namespace, should be changed per session
		name='dating_en',
		display_name='Dating_en',
		app_sequence=['dating_en'],
		num_demo_participants=8,
		participant_label_file='_rooms/n8.txt',
		num_participants_allowed=[8],
		doc="The number of participants must be 8."
	),
	dict(
			id='ME', # default DuckSoup namespace, should be changed per session
			name='meeting_visual_smile',
			display_name='meeting_visual_smile',
			app_sequence=['meeting_visual_smile'],
			num_demo_participants=[8],
			participant_label_file='_rooms/n8.txt',
			num_participants_allowed=[2, 4, 6, 8, 10, 12, 14],
			doc="The number of participants must be a pair number between 2 and 14"
		),
	dict(
			id='ME_N8', # default DuckSoup namespace, should be changed per session
			name='meeting_visual_smile_N8',
			display_name='meeting_visual_smile_N8',
			app_sequence=['meeting_visual_smile_N8'],
			num_demo_participants=8,
			participant_label_file='_rooms/n8.txt',
			num_participants_allowed=[8],
			doc="The number of participants must be 8"
		),					
	dict(
		id='DN', # default DuckSoup namespace, should be changed per session
		name='ducksoup_now',
		display_name='DuckSoup now!',
		app_sequence=['ducksoup_now'],
		num_demo_participants=8,
		participant_label_file='_rooms/n8.txt',
		num_participants_allowed=[2, 4, 6, 8, 10, 12, 14],
		locale="en",
		doc="There must be an even number of participants between 2 and 14."
	),
	
	## Videochat +  Multiperson games
	dict(
			id='initTest', # default DuckSoup namespace, should be changed per session
			name='initTest',
			display_name='initTest',
			app_sequence=['initTest'],
			num_demo_participants=14,
			participant_label_file='_rooms/n8.txt',
			num_participants_allowed=[2, 4, 6, 8],
			doc="The number of participants must be mutiples of 2."
		),
		
		dict(
			id='meeting_visual_smile_N8_brainstorm', 
			name='meeting_visual_smile_N8_brainstorm',
			display_name='meeting_visual_smile_N8_brainstorm',
			app_sequence=['meeting_visual_smile_N8_brainstorm'],
			num_demo_participants=8,
			participant_label_file='_rooms/n8.txt',
			num_participants_allowed=[2, 4, 6, 8, 10, 12, 14],
			doc="The number of participants must be between 2 and 14"
		)
]
			


ROOMS = [
	dict(
		name='room1',
		display_name='Room #1',
		use_secure_urls=True,
		participant_label_file='_rooms/n16.txt',
	),
	dict(
		name='room2',
		display_name='Room #2',
		use_secure_urls=True,
		participant_label_file='_rooms/n16.txt',
	),
	dict(
		name='room3',
		display_name='Room #3',
		use_secure_urls=True,
		participant_label_file='_rooms/n16.txt',
	),
	dict(
		name='room4',
		display_name='Room #4',
		use_secure_urls=True,
		participant_label_file='_rooms/n16.txt',
	),
	dict(
		name='room5',
		display_name='Room #5',
		use_secure_urls=True,
		participant_label_file='_rooms/n16.txt',
	),
	dict(
		name='room6',
		display_name='Room #6',
		use_secure_urls=True,
		participant_label_file='_rooms/n16.txt',
	),
	dict(
		name='room7',
		display_name='Room #7',
		use_secure_urls=True,
		participant_label_file='_rooms/n16.txt',
	),
	dict(
		name='room8',
		display_name='Room #8',
		use_secure_urls=True,
		participant_label_file='_rooms/n16.txt',
	)

]

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
	real_world_currency_per_point=1.00, participation_fee=0.00, doc=""
)

PARTICIPANT_FIELDS = ['image_data', 'audio_source_id', 'video_source_id', 'static_partner_id']
SESSION_FIELDS = []

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = 'en'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'EUR'
USE_POINTS = True

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = os.getenv('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = """ """

SECRET_KEY = '1057662899640'