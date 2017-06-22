
from __future__ import print_function
from os.path import dirname, join
import logging

import pypd
from pypd.errors import BadRequest

logging.basicConfig(level=logging.DEBUG)


# path should be wherever your api.key file exists
path = join(dirname(dirname(__file__)), 'api.key')
pypd.set_api_key_from_file(path)

# set the from_email to an appropriate email for the api key used
from_email = 'jdc@pagerduty.com'

# in this case assuming that there is already a service created
service = pypd.Service.find_one()

# assuming an escalation policy exists as well
escalation_policy = pypd.EscalationPolicy.find_one()

# set some incident data with a incident_key we can use to find it later if
# we want to avoid duplicating until we act on any open incidents
data = {
    'type': 'incident',
    'title': 'incident_demo_incident2',
    'service': {
        'id': service['id'],
        'type': 'service_reference',
    },
    'incident_key': 'incident_demo_key',
    'body': {
        'type': 'incident_body',
        'details': 'testing creating an incident',
    },
    'escalation_policy': {
        'id': escalation_policy['id'],
        'type': 'escalation_policy_reference',
    }
}

# if the incident is already open it will error with BadRequest
try:
    incident = pypd.Incident.create(
        data=data,
        add_headers={'from': from_email, },
    )
except BadRequest:
    incident = pypd.Incident.find(incident_key='incident_demo_key')[-1]

# mergable incident
data_mergable = data.copy()
mergable_key = 'incident_demo_key_mergable'
data_mergable['incident_key'] = mergable_key

try:
    to_merge = pypd.Incident.create(
        data=data_mergable,
        add_headers={'from': from_email, }
    )
except BadRequest:
    to_merge = pypd.Incident.find(incident_key=mergable_key)[-1]

# ack it, snooze it, resolve it... bop it?
print(incident)
print(incident.json)
incident.acknowledge(from_email)
incident.snooze(from_email, duration=3600)
incident.create_note(from_email, 'This is a note!')
incident.merge(from_email, [to_merge, ])
incident.resolve(from_email, resolution='resolved automatically!')
