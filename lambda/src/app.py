import boto3
import pickle
import models

s3_bucket = 'recommendation-pickles'
s3 = boto3.client('s3')


def get_pickle(model_key):
    # Load the pickled model when the Lambda function container starts
    response = s3.get_object(Bucket=s3_bucket, Key=model_key)
    pickled_model = response['Body'].read()
    return pickle.loads(pickled_model)


cosine_sim = get_pickle('cosine-similarities.pkl')
indices = get_pickle('indicies.pkl')
indices_to_name = get_pickle('indicies-to-name.pkl')
model = models.Models(cosine_sim, indices, indices_to_name)


def get_recommendations_by_id_handler(event, context):

    # setting up to handle
    id = event['id']

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
            'body': {
                "recommendations": model.get_recommendations_by_id(int(id))
            }
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
