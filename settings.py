import os

SESSION_CONFIGS = [
	dict(
		id='SC',  # default DuckSoup namespace, should be changed per session
		name='simple_chat',
		display_name='Simple Chat',
		app_sequence=['simple_chat'],
		num_demo_participants=2,
		num_participants_allowed=[2],
		doc="A simple video chat experiment where two participants interact."
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
	## Videochat +  Multiperson games
	dict(
			id='escan_tutorial', # default DuckSoup namespace, should be changed per session
			name='escan_tutorial',
			display_name='escan_tutorial',
			app_sequence=['escan_tutorial'],
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
		),

		dict(id = 'mirror_experiment',
			name = 'mirror_experiment',
			app_sequence = ['mirror_experiment'],
			num_demo_participants = 1,
			participant_label_file = '_rooms/n8.txt',
			num_participants_allowed=[1],
			doc="The number of participants must be 1"),


		dict(id = 'self_feedback_master',
		name = 'self_feedback_master',
		app_sequence = ['self_feedback_master'],
		num_demo_participants = 1,
		participant_label_file = '_rooms/n8.txt',
		num_participants_allowed=[1],
		doc="The number of participants must be 1"),

		dict(id = 'pitching_dyads',
		name = 'pitching_dyads',
		app_sequence = ['pitching_dyads'],
		num_demo_participants = 8,
		participant_label_file = '_rooms/n8.txt',
		num_participants_allowed=[8],
		doc="The number of participants must be 1"),
            
		dict(
			id='technical_prescreen',
			name = 'technical_prescreen',
			display_name='technical_prescreen',
			app_sequence = ['technical_prescreen'],
			num_demo_participants = 1,
			participant_label_file = '_rooms/n8.txt',
			num_participants_allowed=[1],
			doc="The number of participants must be 1 for demo"
		), 
        
        	dict(
			id = 'interactive_psychophysics',
			name = 'interactive_psychophysics',
			app_sequence = ['interactive_psychophysics'],
			num_demo_participants = 6,
			participant_label_file = '_rooms/n8.txt',
			num_participants_allowed=[4,6],
			doc="The number of participants must be 4 or 6"
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