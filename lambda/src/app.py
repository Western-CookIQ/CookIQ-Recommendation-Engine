import json
import boto3
import pickle
import models

s3_bucket = 'recommendation-pickles'
s3 = boto3.resource('s3')


def get_pickle(model_key):
    # Load the pickled model when the Lambda function container starts
    return pickle.loads(s3.Bucket(s3_bucket).Object(model_key).get()['Body'].read())


# cosine_sim = get_pickle('cosine-similarities.pkl')
indices = get_pickle('indicies.pkl')
indices_to_name = get_pickle('indicies-to-name.pkl')
model = models.Models(indices, indices_to_name)


def get_recommendations_by_id_handler(event, context):

    # setting up to handler
    id_value = event['pathParameters']['id']

    try:
        return {
            'statusCode': 200,
            'headers': {
                "Content-Type": 'application/json',
                "Access-Control-Allow-Headers": 'Content-Type,X-Amz- Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                "Access-Control-Allow-Methods": 'OPTIONS,GET',
                "Access-Control-Allow-Credentials": True,
                "Access-Control-Allow-Origin": '*',
                "X-Requested-With": '*'
            },
            'body': json.dumps({
                "recommendations": model.get_recommendations_by_id(int(id_value))
            })
        }
    except:
        return {
            'statusCode': 404,
            'headers': {
                "Content-Type": 'application/json',
                "Access-Control-Allow-Headers": 'Content-Type,X-Amz- Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                "Access-Control-Allow-Methods": 'OPTIONS,GET',
                "Access-Control-Allow-Credentials": True,
                "Access-Control-Allow-Origin": '*',
                "X-Requested-With": '*'
            }
        }
