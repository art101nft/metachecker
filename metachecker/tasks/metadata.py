import os
import requests
from time import sleep

from metachecker.tasks.config import huey, app
from metachecker.models import Collection, Token
from metachecker.factory import db
from metachecker import config


@huey.task()
def fetch_collection_metadata(collection_id: int):
    with app.app_context():
        collection = Collection.query.get(collection_id)
        if collection:
            print(f'[+] Updating collection {collection_id}')
            _f = collection.get_metadata_folder()
            print(_f)
            if not os.path.exists(_f):
                os.makedirs(_f)
                print(f'- created folder {_f}')
            for i in range(collection.start_token_id, collection.end_token_id + 1):
                existing = Token.query.filter(
                    Token.token_id == i,
                    Token.collection_id == collection.id
                ).first()

                fetch = False
                add_db = False
                metadata = None
                token = None
                metadata_uri = f'{collection.get_metadata_folder()}/{i}.json'

                if existing:
                    if os.path.exists(metadata_uri):
                        print(f'| {collection} token {i} already stored, skipping')
                        continue
                    else:
                        fetch = True
                        token = existing
                else:
                    if os.path.exists(metadata_uri):
                        add_db = True
                    else:
                        fetch = True
                        add_db = True

                if add_db:
                    print(f'| adding database item for collection {collection} token {i}')
                    token = Token(
                        collection_id=collection_id,
                        token_id=i
                    )
                    db.session.add(token)
                    db.session.commit()

                if fetch:
                    token_uri = str(collection.metadata_uri) + str(i)
                    print(f'\ fetching metadata for token {i} - {token_uri}')
                    try:
                        metadata = requests.get(token_uri, timeout=30).json()
                        sleep(2)
                    except:
                        print(f'! problem saving collection {collection} token {i}')
                        continue

                    if token and metadata:
                        token.set_metadata_dict(metadata)
                        print(f'/ saved token metadata at {token.get_metadata_path()}')


# @huey.periodic_task(crontab(minute='30', hour='*/2'))
# def fetch_missed():
#     with app.app_context():
#         pass
