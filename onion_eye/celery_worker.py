#!/usr/bin/env python
from onion_eye import celery, create_app

app = create_app()
app.app_context().push()
