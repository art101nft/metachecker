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
                if existing and os.path.exists(existing.get_metadata_path()):
                    print(f'| {collection} token {i} already stored, skipping')
                    continue
                token_uri = str(collection.metadata_uri) + str(i)
                print(f'\ fetching metadata for token {i} - {token_uri}')
                r = None
                try:
                    r = requests.get(token_uri, timeout=20).json()
                    t = Token(
                        collection_id=collection_id,
                        token_id=i
                    )
                    db.session.add(t)
                    db.session.commit()
                    print(f'/ saved token metadata at {t.get_metadata_path()}')
                    t.set_metadata_dict(r)
                    sleep(2)
                except:
                    print(f'! problem saving {collection} token {i}')
                    continue

# @huey.periodic_task(crontab(minute='30', hour='*/2'))
# def fetch_missed():
#     with app.app_context():
#         pass
