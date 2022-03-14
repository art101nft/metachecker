import os, requests
from eth_account.messages import encode_defunct

from web3.auto import w3

from metachecker.models import Token


def verify_signature(message, signature, public_address):
    msg = encode_defunct(text=message)
    recovered = w3.eth.account.recover_message(msg, signature=signature)
    if recovered.lower() == public_address.lower():
        return True
    else:
        return False

def retrieve_token_metadata(token_id):
    token = Token.query.get(token_id)
    if not token:
        print('That token ID does not exist!')
        return False
    _f = token.collection.get_metadata_folder()
    _t = token.get_metadata_path()
    from_local = True
    if not os.path.exists(_f):
        os.makedirs(_f)
        print(f'- created folder {_f}')
    if not os.path.exists(_t):
        token_uri = str(token.collection.metadata_uri) + str(token.token_id)
        print(f'\ fetching metadata for collection {token.collection.id} token {token.token_id} - {token_uri}')
        try:
            metadata = requests.get(token_uri, timeout=30).json()
            token.set_metadata_dict(metadata)
            from_local = False
            print(f'/ saved token metadata at {token.get_metadata_path()}')
        except:
            print(f'! problem saving collection {token.collection.id} token {token_id}')
            return False
    res = token.get_metadata_dict()
    res['from_local'] = from_local
    return res
