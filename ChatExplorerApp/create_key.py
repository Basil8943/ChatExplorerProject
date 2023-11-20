# create_key.py

import os
from pathlib import Path
from secrets import token_bytes
from django.conf import settings

from bson import json_util
from bson.binary import STANDARD
from bson.codec_options import CodecOptions
from pymongo import MongoClient
from pymongo.encryption import ClientEncryption
from pymongo.encryption_options import AutoEncryptionOpts


def create_key():
    secret_file = './Files/secret_key.txt'
    with open(secret_file, 'r') as file:
                key_hex = file.read()

    local_master_key = bytes.fromhex(key_hex)

    # Configure a single, local KMS provider, with the saved key:
    kms_providers = {"local": {"key": local_master_key}}
    csfle_opts = AutoEncryptionOpts(
    kms_providers=kms_providers, key_vault_namespace="SecretkeyDb.__keystore"
    )

    # Connect to MongoDB with the key information generated above:
    with MongoClient(settings.CONNECTION_STRING, auto_encryption_opts=csfle_opts) as client:
        print("Resetting demo database & keystore ...")
        client.drop_database("SecretkeyDb")

        # Create a ClientEncryption object to create the data key below:
        client_encryption = ClientEncryption(
            kms_providers,
            "SecretkeyDb.__keystore",
            client,
            CodecOptions(uuid_representation=STANDARD),
        )

        print("Creating key in MongoDB ...")
        key_id = client_encryption.create_data_key("local", key_alt_names=["sample_demo_key"])


        
        schema  = {
            "bsonType": "object",
            "properties": {
                "firstName": {
                    "encrypt": {
                        "bsonType": "string",
                        # Change to "AEAD_AES_256_CBC_HMAC_SHA_512-Deterministic" in order to filter by ssn value:
                        "algorithm": "AEAD_AES_256_CBC_HMAC_SHA_512-Deterministic",
                        "keyId": [key_id],  # Reference the key
                    }
                },
                "lastName": {
                    "encrypt": {
                        "bsonType": "string",
                        # Change to "AEAD_AES_256_CBC_HMAC_SHA_512-Deterministic" in order to filter by ssn value:
                        "algorithm": "AEAD_AES_256_CBC_HMAC_SHA_512-Deterministic",
                        "keyId": [key_id],  # Reference the key
                    }
                },
            },
            }
        json_schema = json_util.dumps(
        schema, json_options=json_util.CANONICAL_JSON_OPTIONS, indent=2
        )
        Path("json_schema.json").write_text(json_schema)

    
        