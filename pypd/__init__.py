
# Copyright (c) PagerDuty.
# See LICENSE for details.
import logging

from .version import __version__
from .models.ability import can, abilities
from .models.add_ons import AddOn
from .models.escalation_policy import EscalationPolicy
from .models.event import Event, EventV2
from .models.alert import Alert
from .models.incident import Incident
from .models.integration import Integration
from .models.log_entry import LogEntry
from .models.maintenance_window import MaintenanceWindow
from .models.note import Note
from .models.notification import Notification
from .models.on_call import OnCall
from .models.schedule import Schedule
from .models.service import Service
from .models.team import Team
from .models.user import User
from .models.vendor import Vendor

api_key = None
base_url = 'https://api.pagerduty.com'
proxies = None

def set_api_key_from_file(path, set_global=True):
    """Set the global api_key from a file path."""
    with open(path, 'r+b') as f:
        global api_key
        api_key = f.read().strip()
    return api_key
