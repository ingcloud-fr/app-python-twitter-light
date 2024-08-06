import os
import boto3
import json
from botocore.exceptions import NoCredentialsError
from dotenv import load_dotenv

load_dotenv()

def get_secret_from_aws(secret_name):
    region_name = "eu-west-3"  # Remplacez par votre région AWS

    # Créez un client Secrets Manager
    client = boto3.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except NoCredentialsError:
        print("Credentials not available")
        return None

    # Déchiffrez le secret
    secret = get_secret_value_response['SecretString']
    return json.loads(secret)

USE_AWS_SECRETS = os.getenv('USE_AWS_SECRETS', 'False') == 'True'

if USE_AWS_SECRETS:
    secret_name = "dev/mysql/lwitter"
    secret_data = get_secret_from_aws(secret_name)

    if secret_data:
        db_config = {
            'user': os.getenv['DB_USER'],
            'password': secret_data['DB_PASSWORD'],
            'host': os.getenv('DB_HOST', 'localhost'),
            'database': os.getenv('DB_NAME', 'twitter_light')
        }
    else:
        raise Exception("Failed to load secrets from AWS Secrets Manager")
else:
    db_config = {
        'user': os.getenv('DB_USER', 'flask_user'),
        'password': os.getenv('DB_PASSWORD', 'python123#'),
        'host': os.getenv('DB_HOST', 'localhost'),
        'database': os.getenv('DB_NAME', 'twitter_light')
    }

flask_secret_key = os.getenv('FLASK_SECRET_KEY', 'default_secret_key')
