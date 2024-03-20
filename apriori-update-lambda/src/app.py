import json
import boto3
import pickle
import psycopg2
import pandas as pd
from apyori import apriori
import os


s3_bucket = 'recommendation-pickles'
s3 = boto3.resource('s3')

# Helper function to fetch the pickled files from S3
def get_pickle(model_key):
    # Load the pickled model when the Lambda function container starts
    return pickle.loads(s3.Bucket(s3_bucket).Object(model_key).get()['Body'].read())

# Database connection parameters
dbname = "initial_db"
user = "postgres"
password = "cookiq123"
host = "database-1.cj4mmp0k4i3t.us-east-2.rds.amazonaws.com"
port = "5432"

# Construct the connection string
connection_string = f"dbname={dbname} user={user} password={password} host={host} port={port}"


def get_recommendations_by_id_handler(event, context):
    connection = None
    cursor = None

    apriori_prev_df = get_pickle('apriori-df.pkl')

    # convert rating_dict column from string to list
    if isinstance(apriori_prev_df['rating_dict'][0], str):
        apriori_prev_df['rating_dict'] = apriori_prev_df['rating_dict'].apply(eval)

    try:
        # Establish a connection to the PostgreSQL database
        connection = psycopg2.connect(connection_string)
        print("Connected to the database!")

        # Create a cursor object to interact with the database
        cursor = connection.cursor()

        # Example: Execute a query using data from the Lambda event
        query = f"SELECT user_id, recipe_id, rating FROM meal WHERE rating >= 0"
        cursor.execute(query)

        # Fetch all rows from the result set
        rows = cursor.fetchall()

        # start to iterate through rows to form update set    
        formatted_recommendations = [{'user_id': item[0], 'data': {'recipe_id': item[1], 'rating': int(item[2])}} for item in rows]

        for recommendation in formatted_recommendations:
            user_id = recommendation['user_id']
            new_dict = recommendation['data']
            print("new_dict", new_dict)

            # find row index for associated user_id
            if user_id not in apriori_prev_df['user_id'].values:
                new_row = {'user_id': user_id, 'rating_dict': [new_dict]}
                new_row_df = pd.DataFrame(columns=apriori_prev_df.columns)
                new_row_df = new_row_df.append(new_row, ignore_index=True)
                apriori_prev_df = apriori_prev_df.append(new_row_df, ignore_index=True)
    
            else:
                # find row index for associated user_id
                row_index = apriori_prev_df.index[apriori_prev_df['user_id'] == user_id][0]

                #appen new_dict to rating_dict of associated user_id
                apriori_prev_df.at[row_index, 'rating_dict'].append(new_dict)
        
        # update the apriori-df.pkl file with the new rating_dict
        df_file_path = '/tmp/apriori-df.pkl'
        apriori_prev_df.to_pickle(df_file_path)

        recipe_listing = apriori_prev_df['rating_dict']

        transformed_recipe_listing = []
        for i in recipe_listing:
            sub_list = []
            for j in i:
                sub_list.append(j['recipe_id'])

            transformed_recipe_listing.append(sub_list)

        # transactions, min support, min confidence, min lift parameters to get relevant rules
        rules = apriori(transactions = transformed_recipe_listing, min_support = 10/9955, min_confidence = 0.2, min_lift = 3, min_length=1,max_length = 2)
        results = list(rules)

        def apriori_table(results):
            lhs         = [tuple(result[2][0][0])[0] for result in results]
            rhs1        = [tuple(result[2][0][1])[0] for result in results]
            supports    = [result[1] for result in results]
            return list(zip(lhs, rhs1, supports))
        
        apriori_recipe_df = pd.DataFrame(apriori_table(results), columns = ['Base Product', 'Add Product', 'Support'])

        # now we need to replace the current apriori-rules.pkl with this new file
        apriori_recipe_df.sort_values(by='Support', ascending=False, inplace=True)
        file_path = '/tmp/apriori-rules.pkl'
        apriori_recipe_df.to_pickle(file_path) 

        # Upload the new apriori-rules.pkl file to S3
        s3.Bucket(s3_bucket).upload_file(df_file_path, 'apriori-df.pkl')
        s3.Bucket(s3_bucket).upload_file(file_path, 'apriori-rules.pkl')

    except psycopg2.Error as e:
        print("Unable to connect to the database or execute query.")
        print(e)
    finally:
        # Close the cursor and the connection in the finally block to ensure cleanup
        if cursor:
            cursor.close()
        if connection:
            connection.close()
            print("Connection closed.")

    response = {
        'statusCode': 200,
        'headers': {
            "Content-Type": 'application/json',
            "Access-Control-Allow-Headers": 'Content-Type,X-Amz- Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            "Access-Control-Allow-Methods": 'OPTIONS,GET',
            "Access-Control-Allow-Credentials": True,
            "Access-Control-Allow-Origin": '*',
            "X-Requested-With": '*'
        },
    }

    return response
