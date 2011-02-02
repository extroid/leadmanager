# DJANGO IMPORTS
from django.conf import settings
from msafactory import post_lead, parse_lead_file
POST_PROCEDURE = getattr(settings, "MSA_POST_PROCEDURE", post_lead)
CSV_PARSER = getattr(settings, "MSA_CSV_PARSER", parse_lead_file)

