sofa
====

Setup
-------------
1. `cd PROJECTS_DIR`
2. `virtualenv ENV && cd ENV`
3. `source bin/activate`
3. `git clone https://github.com/maxdeviant/sofa && cd sofa`
5. `pip install -r requirements.txt`

###Settings
In `settings.py`:

```
DB_USERNAME='admin'
DB_PASSWORD='default'
```

###Database
`python -m db.init`