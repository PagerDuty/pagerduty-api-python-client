# pypd - PagerDuty Python API Client
A client in Python for PagerDuty's v2 API.

## How Do
Yes, how do. The ultimate question in quickstart.
```python
import pypd
pypd.api_key = "SOMESECRETAPIKEY"

# fetch some dataz
incidents = pypd.Incidents.find(maximum=10)

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

# find users
user = pypd.User.find_one(email="jdc@pagerduty.com")
```

## Notes
Currently the following models are not complete, but will be shortly!
- `Schedule`
- `Service`
- `Team`
- `User`

If you need some embedded properties that don't exist, take a look at `LogEntry` or `Incident` model classes.

## Tests
Run all the tests (unittests only currently) with:
```sh
python test/runtests.py [-vvv]
```

## Links

An asynchronous port of this library for [Twisted](http://twistedmatrix.com) exists [txpypd](https://github.com/PagerDuty/txpypd) and is on it's way to catching up now.

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
