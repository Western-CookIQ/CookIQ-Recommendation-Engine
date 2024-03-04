import json
import pandas
import boto3
import pickle

# S3 bucket details
s3_bucket = 'recommendation-pickles'
s3 = boto3.resource('s3')

def get_pickle(model_key):
    # Load the pickled model when the Lambda function container starts
    return pickle.loads(s3.Bucket(s3_bucket).Object(model_key).get()['Body'].read())

# fetch the pickled files from S3
apriori_rules_df = get_pickle('apriori-rules.pkl')
recipes_df = get_pickle('recipes-subset.pkl')
cosine_similarities = get_pickle('cosine-similarities.pkl') # STILL REQUIRED

def get_recommendations_handler(event, context):
    # get the recipe index from the path parameter
    given_recipe_index = int(event['pathParameters']['id'])

    # get the top 30 similar recipes
    remaining = 30 - min(30,len(apriori_rules_df[apriori_rules_df['Base Product'] == given_recipe_index]))
    
    # get the top remaining similar recipes
    sim_scores = list(enumerate(cosine_similarities[cosine_similarities['id'] == given_recipe_index]))
    top_similar = sim_scores[1:remaining+1]

     # Get the recipe indices and corresponding recipe similarity score
    recipe_indices = [i[0] for i in top_similar]
    recipe_similarity_scores = [i[1] for i in top_similar]

    recommendations_df = recipes_df['name'].iloc[recipe_indices].to_frame().reset_index()
    recommendations_df['score'] = recipe_similarity_scores

    # construct final response object
    result_data = recommendations_df.to_dict(orient='records')

    response = {
        'statusCode': 200 if result_data else 404,
        'headers': {
            "Content-Type": 'application/json',
            "Access-Control-Allow-Headers": 'Content-Type,X-Amz- Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            "Access-Control-Allow-Methods": 'OPTIONS,GET',
            "Access-Control-Allow-Credentials": True,
            "Access-Control-Allow-Origin": '*',
            "X-Requested-With": '*'
        },
    }

    if result_data:
        response['body'] = json.dumps({
            'recommendations': result_data
        })

    return response