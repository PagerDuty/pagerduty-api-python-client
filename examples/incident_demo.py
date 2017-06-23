
from __future__ import print_function
from os.path import dirname, join
import logging
from time import sleep

from pprint import pprint

import pypd
from pypd.errors import BadRequest

# turn logging on debug so we can see details about HTTP requests
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
pprint(incident)
pprint(incident.json)
incident.acknowledge(from_email)
incident.snooze(from_email, duration=3600)
incident.create_note(from_email, 'This is a note!')
incident.merge(from_email, [to_merge, ])

# before we trigger an event get all currently triggered incidents
triggered_incidents = pypd.Incident.find(statuses=['triggered', ])

# let's see if events and alerts work!
pypd.EventV2.create(data={
    'routing_key': '64e61052453e4ec0a3b42e93ac235375',
    'event_action': 'trigger',
    'payload': {
        'summary': 'this is an error event!',
        'severity': 'error',
        'source': 'pypd bot',
    }
})

# wait for our events to trigger incidents
while True:
    incidents = pypd.Incident.find(statuses=['triggered', ])
    if len(incidents) > len(triggered_incidents):
        break
    pprint('Sleeping for 1 second...')
    sleep(1)

# find the new incidents because they will have alerts since they were event
# generated
triggered_ids = [i['id'] for i in triggered_incidents]
incident_ids = [i['id'] for i in incidents]
new_ids = set(triggered_ids).union(set(incident_ids))
new_incidents = filter(lambda i: i['id'] in new_ids, incidents)
new_incident = new_incidents[0]
alerts = new_incident.alerts()

# try some alert actions
alert = alerts[0]
pprint(alert.json)
pprint(alert.resolve(from_email))


for i in incidents:
    # skip the one we resolved earlier because it will only have 1 alert
    if i['id'] == new_incident['id']:
        continue
    i.resolve(from_email=from_email, resolution='resolved automagically!')

# resolve and finish up
incident.resolve(from_email, resolution='resolved automatically!')
