
from __future__ import print_function

from os.path import dirname, join
from pprint import pprint, pformat


import pypd
import clean


result = None
all_run_lines = []


def run(s, exit_on_exception=True, pluck=None):
    all_run_lines.append(s)
    print('\n```\n>>> %s' % s)
    try:
        exec(s)
    except Exception as e:
        print('ERROR: %s' % e)
        if exit_on_exception:
            print('The demo is broken! So sad :(')
            exit()
    print('\n```\n')
    output = locals()

    if pluck is None:
        return output

    return locals().get(pluck)


def wait(s='Press enter to continue.\n'):
    try:
        return raw_input(s)
    except KeyboardInterrupt:
        exit()
    except:
        pass


steps = """
Let's make Python great again!

We are going to:
- use a custom api key
- make a user
- make a team for the user
- add the user to the team
- make a escalation policy
- create a service using the escalation policy we created
- acknowledge any open incidents
- delete the user (this shouldn't work!)
- delete the team
- delete the service
- delete the escalation policy
- create a user (same email as earlier, should not work!)
- delete the user (this should work now!)
"""

clean.clean()

path = join(dirname(dirname(dirname(__file__))), 'api.key')
with open(path, 'r+b') as f:
    api_key = f.read()

user_data = {
    'type': 'user',
    'name': 'Donald Drumpf',
    'color': 'green',
    'role': 'user',
    'job_title': 'Wall-Builder',
    'description': 'Making Python awesome again, one alert at a time!',
}

contact_data = {
    "id": "string",
    "summary": "string",
    "type": "SMS_contact_method",
    "self": "string",
    "html_url": "string",
    "label": "Mobile",
    "address": "2898080930",
    "country_code": 1,
}

ep_data = {
    'type': 'escalation_policy',
    'name': 'Political Escalation Policy',
    'escalation_rules': [
        {
            'escalation_delay_in_minutes': 30,
            'targets': [],
        }
    ],
    'repeat_enabled': True,
    'num_loops': 2,
    'teams': []
}

service_data = {
    'type': 'service',
    'name': 'USA Political Failure Detection Service',
    'description': 'To detect on how well (or poorly) the USA peoples are '
                   'doing regarding their POTUS',
    'auto_resolve_timeout': 60 * 60 * 4,  # 60s * 60m * 4h,
    'acknowledgment_timeout': 60 * 10,  # 60s * 10m
    'status': 'active',
    'incident_urgency_rule': {
        'type': 'constant',
        'urgency': 'high',
    },
}

team_data = {
    'name': 'Presidents of the United States of America',
    'description': 'Only the best of the best. Only the Donalds.'
}

print(steps)
wait()
print('Setting a custom api key\n===\n')
run('pypd.api_key = api_key')
wait()
# print('Shim the API because it is currently broken *coughcough*')
# run('pypd.base_url = "https://pdt-jdc.pagerduty.com/api/v1"')
# wait()


# --- make user
print('Making a user\n===\n')
user_data['email'] = wait('Enter an email: ') or 'jdc+drumpf@pagerduty.com'

print('\nWe know *him*. We already have his details...\n')
print('Creating a user with details:\n')
formatted = pformat(user_data)
print('user_data = \n%s' % formatted)
results = run('user = pypd.User.create(data=user_data, '
              'from_email="jdc@pagerduty.com")')
user = results['user']
pprint(user.json)
print('\n\n')
wait()

# --- add contact info for that user
print('Create a contact method for the demo:\n')
contact_data['address'] = wait('Enter phone number for SMS contact: ') or \
    '2898080930'
contact_data['number'] = contact_data['address']
contact_data['phone_number'] = contact_data['address']
print('Creating a contact method with details:\n')
formatted = pformat(contact_data)
print('contact_data = \n%s' % formatted)
results = run('result = user.create_contact_method(contact_data)')
pprint(results['result'])
print('\n\n')
wait()


# --- make team for the user
print('Make a team for the user\n===\n')
print('Now create a team for %s' % (user,))
team_data['name'] = wait('Enter team name: ') or team_data['name']
print('Creating team with details:\n')
print('team_data = \n%s' % (pformat(team_data)))
results = run('team = pypd.Team.create(data=team_data)')
team = results['team']
pprint(team.json)
print('\n\n')
wait()
# --- add the user to the team
print('Add the user to the team\n===\n')
print('Now add %s to %s' % (user, team))
results = run('team.add_user(user)')
wait()


# --- make escalation policy
print('Make a Escalation Policy\n===\n')
print('Now lets create an Escalation Policy for %s' % (user,))
ep_data['name'] = wait('Enter an escalation policy name: ') or 'POTUS'
ep_data['escalation_rules'][0]['targets'].append({
    'id': user.id,
    'type': 'user',
})
print('Creating an EscalationPolicy with details:\n')
formatted = pformat(ep_data)
print('ep_data = \n%s' % formatted)
results = run('ep = pypd.EscalationPolicy.create(data=ep_data)')
ep = results['ep']
pprint(ep.json)
print('\n\n')
wait()


# --- create service
print('Create a service using the escalation policy we created\n===\n')
print('Now create a service using  %s'
      % (ep,))
service_data['name'] = wait('Enter service name: ') or service_data['name']
service_data['escalation_policy'] = {
    'id': ep.id,
    'type': 'escalation_policy',
}
print('Creating a service with details:\n')
formatted = pformat(service_data)
print('service_data = \n%s' % formatted)
results = run('service = pypd.Service.create(data=service_data)')
service = results['service']
pprint(service.json)
print('\n\n')
wait()


# --- bonus
print('BONUS: Find the escalation policies that Mr. Drumpf is on\n===\n')
results = run('eps = pypd.EscalationPolicy.find(user_ids=[user.id])')
print(results['eps'])
print('\n\n')
ep = results['eps'][0]
wait()


# --- bonus 2
print('ANOTHER BONUS: find all users on my account except Mr. Drumpf\n===\n')
results = run('users = pypd.User.find(exclude=("jdc+drumpf@pagerduty.com",))')
print(results['users'])
print('\n\n')
wait()


# --- bonus 3
print('Wait, there\'s more! Services related to an Escalation Policy are '
      'free if you call right now!\n===\n')
results = run('services = ep.services')
print(results['services'])
print('\n\n')
wait()


# --- ack any incidents that are open
print('Acknowledge any incidents that are open for %s\n===\n' % (service,))
results = run('incidents = pypd.Incident.find(service_ids=(service.id,))')
incidents = results['incidents']
print(incidents)
run('[i.resolve(from_email="%s", resolution="Build wall.") for i in '
    'incidents]' % user.email)
print('\n\n')
wait()


# --- delete user expected to fail
print('Delete the user (this shouldn\'t work!)\n===\n')
results = run('user.remove()', exit_on_exception=False)
print('\nOh noes! Let\'s do things by the book (for a change) Mr. Drumpf')
wait()

# --- delete team
print('Delete the team\n===\n')
results = run('team.remove()')
print('\n\n')
wait()

print('Delete the service\n===\n')
results = run('service.remove()')
print('\n\n')
wait()


# --- delete ep
print('Delete escalation policy\n===\n')
results = run('ep.remove()')
print('\n\n')
wait()


# --- create duplicate user expected to fail
print('Create a user (same email as earlier, should not work!)\n===\n')
results = run('pypd.User.create(data=user_data)', exit_on_exception=False)
print('Erroring as expected! Next time... walls!\n')
print('\n\n')


# --- delete the user for realz
print('Delete the user (this should work now!)')
results = run('user.remove()')
print('\n\n')


# --- conclude
print('Guess it wasn\'t meant to be Mr. Drumpf')
print('Thanks for watching.\n\nFull lines run:\n')
print('\n'.join(all_run_lines))
print('\n\n')
wait('Press any key to exit.')
exit()
