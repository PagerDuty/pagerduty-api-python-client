# pypd - PagerDuty Python API Client
A client in Python for PagerDuty's v2 API.

#### This is a community supported repository
This repository is not an offical product of PagerDuty but aims to be an
effective tool for developers to use the PagerDuty API. If you have concerns
or issues you are welcome to bring them up as an issue on the repository, or
we would be even happier to accept your pull requests! Happy coding :)

Now available on PyPI https://pypi.python.org/pypi/pypd

## How Do
Yes, how do. The ultimate question in quickstart.

Make sure that you have installed requirements with pip
```sh
pip install -r requirements.txt
```

Then get cracking
```python
import pypd
pypd.api_key = "SOMESECRETAPIKEY"

# fetch some dataz
incidents = pypd.Incident.find(maximum=10)

# how do dataz?
ep = pypd.EscalationPolicy.find_one()
print ep['id']
print ep.get('name')
print ep.json  # not a string, a json-compat dict
print ep.__json__()  # a json encoded string, json encoder interface compat
print ep._data  # raw data, best not to access it this way!

# nice embedded property things
incident = pypd.Incident.find_one()
log_entries = incident.log_entries()
alerts = incident.alerts()

# incident actions
incident.snooze(from_email='jdc@pagerduty.com', 3600) # snooze for an hour
incident.resolve(from_email='jdc@pagerduty.com', resolution='We solved a thing')
incident.merge(from_email='jdc@pagerduty.com', [another_incident, ])
incident.create_note(from_email='jdc@pagerduty.com', 'Duly noted.')

# find users
user = pypd.User.find_one(email="jdc@pagerduty.com")

# create an event
pypd.Event.create(data={
    'service_key': 'YOUR_INTEGRATION_KEY',
    'event_type': 'trigger',
    'description': 'this is a trigger event!',
    'contexts': [
          {
              'type': 'link',
              'href': 'http://acme.pagerduty.com',
              'text': 'View on PD',
          },
    ],
})

# create a version 2 event
pypd.EventV2.create(data={
    'routing_key': 'YOUR_INTEGRATION_KEY',
    'event_action': 'trigger',
    'payload': {
        'summary': 'this is an error event!',
        'severity': 'error',
        'source': 'pypd bot',
    }
})
```

If you need more examples head to [incident_demo.py](./examples/incident_demo.py).

## Notes
All models **should** be complete CR-D complete, with the missing *update* method. Soon to be fixed.

If you need some embedded properties that don't exist, take a look at `LogEntry` or `Incident` model classes.

There was some stagnation on the pull requests here. No longer! Thanks for being patient.

## Tests
Make sure you have `tox` installed
```sh
pip install -r test_requirements.txt

# or

pip install tox
```

Run all the tests (unittests only currently) with:
```sh
tox
```

## Proxy Support
The underlying HTTP client library - [requests](python-requests.org) - allows for two mechanisms to set the proxies.

You could set it via environment variables:

```sh
export HTTP_PROXY=http://myproxy.domain.tld:8080
export HTTPS_PROXY=http://myproxy.domain.tld:8080
```

The other method is to add the proxy details in your code, like this:

```python
import pypd
pypd.api_key = "SOMESECRETAPIKEY"
pypd.proxies = {'http': 'http://myproxy.domain.tld:8080', 'https': 'http://myproxy.domain.tld:8080'}
```

**Note:** The proxies configured inside your code will have preference over the proxies set in the environment variables.

Read: [The `requests` module and it's support for proxies](http://docs.python-requests.org/en/master/user/advanced/#proxies)

## Links

Do you develop **twisted** applications? An asynchronous port of this library
for [Twisted](http://twistedmatrix.com) exists
[txpypd](https://github.com/PagerDuty/txpypd) and is on it's way to
catching up now.

## Contributing
All help is welcome. Unittests are great to have more of. Suggestions welcome.

## Copyright
All the code in this distribution is Copyright (c) 2016 PagerDuty.


pypd is availabe under the MIT License. The [LICENSE](LICENSE) file has
the complete details.


## Warranty
> THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
> IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
> FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
> AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
> LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
> OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
> THE SOFTWARE.

The [LICENSE](LICENSE) file has the complete details.
