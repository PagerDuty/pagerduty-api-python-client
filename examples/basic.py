""" 
DEPRECATED. Does not work.

"""
from __future__ import print_function

import os
import os.path

import pprint

import pypd
from pypd.errors import BadRequest


def printsep():
    print('---\n')

def require_enter():
    try:
        input('Press enter to continue.')
    except:
        pass
    printsep()

user_data = {
    'type': 'user',
    'name': 'PagerDuty HackDay',
    'email': 'jdc+hackday@pagerduty.com',
    'color': 'green',
    'role': 'user',
    'marketing_opt_out': False,
    'job_title': 'Sudo-Vibe Specialist',
    'description': 'Make python awesome again!',
    'avatar_url': 'https://encrypted-tbn2.gstatic.com/images?q=tbn:ANd9GcRVwI'
                  'BiSHMwICK7nn_BJ4uXqJl1JChCrj2eEbfI0tdToD618xVQzQ'
}

print('Let\'s make Python great again!')
steps = """
1) Create a user with username 'jdc+hackday@pagerduty.com', let's call it JDHD
2) Create an escalation policy that JDHD will be apart of
3) Add the account (pick one if multiple) to the escalation policy as the 
   second responder
4) Create a team called 'The Trumpedwagon'
5) Add JDHD to 'The Trumpedwagon' team
"""
print(steps)

require_enter()

path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'api.key')
with open(path, 'r+b') as f:
    pypd.api_key = f.read()
    pypd.base_url = 'https://pdt-jdc.pagerduty.com/api/v1'

def create_user():
    print('Attempting to create user \'%s\'...' % (user_data['email']))

    try:
        user = pypd.User.create(data=user_data, from_email='jdc@pagerduty.com')
        print('\n\n```')
        print('pypd.User.create()')
        print(user)
        print('\n```\n')

        print('Success! User created for \'%s\' with id \'%s\'' % \)
              (user.email, user.id)
        print('\n\n```')
        print('user.json()')
        pprint.pprint(user.json())
        print('\n```\n\n')

        require_enter()
        return user

    except BadRequest as e:
        for err in e.errors:
            if 'Email' in err:
                print('\nOh noes! His email was already taken, lets delete it.')
                require_enter()

                print('Finding id for user \'%s\'' % (user_data['email']))
                print('\n\n```')
                print('pypd.User.find_one(query=user_data[\'email\'])')
                user = pypd.User.find_one(query=user_data['email'])
                print(user)
                print('\n```\n')

                print('User found! Deleting \'%s\' with id=%s' % \)
                      (user_data['email'], user['id'])

                require_enter()

                print('\n\n```')
                print('pypd.User.delete(user[\'id\'])')
                print(pypd.User.delete(user['id']))
                print('\n```\n')

                print('User deleted!')
                require_enter()
                return create_user()
            else:
                print(dir(e))

user = create_user()

def create_policy():
    escalation_policy = {
        'type': 'escalation_policy',
        'summary': 'The policy of a winner; Making Python great again',
        'name': '#Win2016',
        'escalation_rules': [
            {
                'escalation_delay_in_minutes': 5,
                'targets': [
                    {
                        'id': user.id,
                        'type': 'user',
                        'summary': '0 to 100, real quick'
                    },
                ]
            }
        ]
    }
    print('Creating escalation policy')
    print('\n\n```')
    print('pypd.EscalationPolicy.create(from=\'jdc@pagerduty.com\', '
          'escalation_policy)'
    ep = pypd.EscalationPolicy.create(escalation_policy)
    print(ep)
    print('\n```\n')
    print('Policy created!')
    require_enter()

policy = create_policy()
