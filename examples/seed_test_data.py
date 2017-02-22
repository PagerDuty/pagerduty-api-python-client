
import os.path
import json

import pypd


API_KEY = "w_8PcNuhHa-y3xYdmc1x"


if __name__ == "__main__":
    pypd.api_key = API_KEY

    basepath = path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        'test',
        'data',
    )

    path = os.path.join(basepath, 'sample_escalation_policies.json')
    with open(path, 'w') as f:
        eps = pypd.EscalationPolicy.find()
        raw = [ep.json for ep in eps]
        f.truncate()
        f.write(json.dumps(raw, indent=4))
        f.flush()

    path = os.path.join(basepath, 'sample_services.json')
    with open(path, 'w') as f:
        services = pypd.Service.find()
        raw = [service.json for service in services]
        f.truncate()
        f.write(json.dumps(raw, indent=4))
        f.flush()
