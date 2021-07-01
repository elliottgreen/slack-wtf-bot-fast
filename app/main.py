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

    # Retrieve the contents of the CSV at DATA_URL
    raw_data = requests.get(settings.DATA_URL)

    # Decode utf-8 data to ascii text
    decoded_data = raw_data.content.decode('utf-8')

    # Parse decoded data into a table by newline breaks
    reader = csv.reader(decoded_data.split('\n'), delimiter=',')

    # Seperate parsed data into a list
    all_definitions = [row for row in reader if len(row) > 1]

    # Instantiate an empty dictionary to hold 
    lexicon = {}

    # Loop to build terms from csv at DATA_URL
    for terms in all_definitions:

        # Force the acronym to be in lower case
        acroynm = terms[0].lower()

        # Drop any leading or training spaces
        definition = terms[1].strip()

        # Add the context of the acronym if provided. 
        # Leave the context blank otherwise. 
        if len(terms[2]) > 0:
            context = "\n\t- " + terms[2].strip()
        else:
            context = ''

        # Add the notes of the acronym if provided. 
        # Leave the notes blank otherwise. 
        if len(d[3]) > 0:
            notes = "\n\t- " + terms[3].strip()
        else:
            notes = ''

        #Build the full definition which includes:
        # 1. Definition
        # 2. Context
        # 3. Notes
        full_data = "{}{}{}".format(definition, context, notes)

        # Check the lexicon dictionary built earlier for term 
        # Set return type as None with get method
        existing = lexicon.get(acroynm, None)

        # Add term to dict if it is not already 
        # full_data is cast as a list in order to squeeze into the dict
        if not existing:
            lexicon[acroynm] = [full_data]

        else:
            lexicon[acroynm] = existing + [full_data]

    try:

        acroynm_defined = lexicon[text.lower()]

        if len(acroynm_defined) > 1:
            response = ' - ' + '; \n - '.join(acroynm_defined)

        else:
            response = ' - ' + acroynm_defined[0]

        response = text + '\n' + response

    # If the provided acronym is not found, return this string. 
    except KeyError:
        response = """
        Entry for '{}' not found! Acronyms may be added at
        https://github.com/elliottgreen/slack-wtf-bot-acronyms
        """.format(text)

    return response
