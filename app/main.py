import csv
import config
import requests
from functools import lru_cache
from fastapi import (
        FastAPI,
        Depends,
        Form,
        HTTPException,
        status
        )

fap = FastAPI()

@lru_cache()
def get_env_vars():
    return config.Settings()

@fap.get('/info')
async def info(settings: config.Settings = Depends(get_env_vars)):
    return{ "Slack Token" : settings.SLACK_TOKEN,
            "Data URL" : settings.DATA_URL,
            }

@fap.post('/define')
async def define(text: str = Form(...), token: str = Form(...), 
        settings: config.Settings = Depends(get_env_vars)):


    if text is None or token is None:
        return make_response('Improper request.', http.HTTPStatus.BAD_REQUEST)
    if token != settings.SLACK_TOKEN:
        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not Authorized",
                )

    raw = requests.get(settings.DATA_URL)

    decoded = raw.content.decode('utf-8')

    reader = csv.reader(decoded.split('\n'), delimiter=',')

    data = [r for r in reader if len(r) > 1]

    term_dict = {}

    for d in data:

        acroynm = d[0].lower()
        definition = d[1].strip()
        context = ''
        notes = ''
        if len(d[2]) > 0:
            context = "\n\t- " + d[2].strip()
        if len(d[3]) > 0:
            notes = "\n\t- " + d[3].strip()
        full_data = "{}{}{}".format(definition, context, notes)

        existing = term_dict.get(acroynm, None)

        if not existing:
            term_dict[acroynm] = [full_data]

        else:
            term_dict[acroynm] = existing + [full_data]

    try:

        acroynm_defined = term_dict[text.lower()]

        if len(acroynm_defined) > 1:
            response = ' - ' + '; \n - '.join(acroynm_defined)

        else:
            response = ' - ' + acroynm_defined[0]

        response = text + '\n' + response

    except KeyError:
        response = """
        Entry for '{}' not found! Acronyms may be added at
        https://github.com/elliottgreen/slack-wtf-bot-acronyms
        """.format(text)

    return response
