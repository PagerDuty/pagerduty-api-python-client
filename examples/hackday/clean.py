# Copyright (c) PagerDuty.
# See LICENSE for details.
from __future__ import print_function

import pypd
import preload


def clean():
    preload.preload()  # only sets api key

    users = pypd.User.find(
        exclude=('jdc@pagerduty.com', 'jdc+dummy@pagerduty.com',))

    for user in users:
        incidents = pypd.Incident.find()

        for i in incidents:
            if i['status'] != 'resolved':
                i.resolve(from_email=user.email,)

        eps = pypd.EscalationPolicy.find(user_ids=[user.id, ])
        for ep in eps:
            for service in ep.services:
                service.remove()
            ep.remove()

        schedules = pypd.Schedule.find(user_ids=[user.id, ])
        for s in schedules:
            s.remove()

        user.remove()

    teams = pypd.Team.find()
    for team in teams:
        if team['name'] == 'Test Team':
            continue
        team.remove()

    users = pypd.User.find()

    if 'jdc+dummy@pagerduty.com' not in [u.email for u in users]:
        dummy_user_data = {
            'type': 'user',
            'name': 'Does Nothing',
            'color': 'green',
            'job_title': 'Professional Squatter',
            'description': 'I just sit unintended for use.',
            'email': 'jdc+dummy@pagerduty.com',
        }

        pypd.User.create(data=dummy_user_data, from_email=users[0].email)

if __name__ == "__main__":
    clean()
