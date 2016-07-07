# Copyright (c) PagerDuty.
# See LICENSE for details.
from __future__ import print_function

import pypd
from hackday import preload


def printsep():
    print('---\n')


preload.preload()


users = pypd.User.find()
emails = [u.email for u in users]
for email in emails:
    u = pypd.User.find_one(email=email)
    print(u.email, email)

policies = pypd.EscalationPolicy.find()
print(policies)
printsep()

policy = pypd.EscalationPolicy.fetch(policies[0].id)
print(policy)
print(policy.json())
printsep()

incidents = pypd.Incident.find()
print(incidents)
printsep()

incident = pypd.Incident.fetch(incidents[0].id)
print(incident)
print(incident.json())
printsep()
