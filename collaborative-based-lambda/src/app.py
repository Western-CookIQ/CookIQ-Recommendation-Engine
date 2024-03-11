import json
import pandas as pd
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

def get_recipe_id(recipe_index):
    return int(recipes_df['id'].iloc[recipe_index])

def get_recommendations_handler(event, context):
    # get the recipe index from the path parameter
    given_recipe_index = int(event['pathParameters']['id'])

    # get the top 30 similar recipes
    remaining = 20 - min(20,len(apriori_rules_df[apriori_rules_df['Base Product'] == given_recipe_index]))

    recipe_apriori_df = pd.DataFrame(columns = ['index', 'name', 'score'])

    if remaining < 20:

        df = apriori_rules_df[apriori_rules_df['Base Product'] == given_recipe_index]
        
        # iterate through rows of the dataframe
        for _, row in df.iterrows():

            
            apriori_recipe_id = row['Add Product']
            
            df_id = recipes_df[recipes_df['id'] == apriori_recipe_id]['Unnamed: 0'].values[0]
            recipe_name = recipes_df[recipes_df['id'] == apriori_recipe_id]['name'].values[0]
            recipe_score = row['Support']
            

            values = [df_id, recipe_name, recipe_score]

            recipe_apriori_df.loc[len(recipe_apriori_df)] = values

    recipe_apriori_df['type'] = 'apriori'
    recipe_ids = [get_recipe_id(i) for i in recipe_apriori_df['index']]
    recipe_apriori_df['id'] = recipe_ids
        
    # Select columns containing ids and scores
    id_columns = [col for col in cosine_similarities.columns if col.startswith('id_')]
    score_columns = [col for col in cosine_similarities.columns if col.startswith('score_')]

    # list to contain pairs of ids and similarity scores
    output = []

    # iterate through ids and scores together
    for id_col, score_col in zip(id_columns, score_columns):

        # recipe ids
        recipe_id = cosine_similarities[cosine_similarities['id'] == given_recipe_index][id_col].values[0]

        # get index in dataframe from recipe id
        df_id = recipes_df[recipes_df['id'] == recipe_id]['Unnamed: 0'].values[0]

        # recipe similarity score
        recipe_score = cosine_similarities[cosine_similarities['id'] == given_recipe_index][score_col].values[0]

        # append the pair of df index and rceipe score to list
        output.append([df_id, recipe_score])


    # Get the scores of the remaining (0-30) most similar recipes
    output = output[0:remaining]

    # Get the recipe indices and corresponding recipe similarity score
    recipe_indices = [i[0] for i in output]
    recipe_similarity_scores = [i[1] for i in output]
    recipe_ids = [get_recipe_id(i) for i in recipe_indices]

    recommendations_df = recipes_df['name'].iloc[recipe_indices].to_frame().reset_index()
    recommendations_df['score'] = recipe_similarity_scores
    recommendations_df['id'] = recipe_ids

    recommendations_df['type'] = 'cosine_sim'
  
    final_recommendation_df = pd.concat([recipe_apriori_df, recommendations_df])
    result_data = final_recommendation_df.to_dict(orient='records')

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