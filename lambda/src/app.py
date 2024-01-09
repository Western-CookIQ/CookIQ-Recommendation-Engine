import json
import boto3
import pickle
import models
import psycopg2

s3_bucket = 'recommendation-pickles'
s3 = boto3.resource('s3')


def get_pickle(model_key):
    # Load the pickled model when the Lambda function container starts
    return pickle.loads(s3.Bucket(s3_bucket).Object(model_key).get()['Body'].read())


# FETCH FROM PICKLES

# cosine_sim = get_pickle('cosine-similarities.pkl')
# indices = get_pickle('indicies.pkl')
# indices_to_name = get_pickle('indicies-to-name.pkl')
# model = models.Models(cosine_sim, indices, indices_to_name)

# FETCH FROM SQL

# Replace these values with your own database connection details
dbname = "initial_db"
user = "postgres"
password = "cookiq123"
host = "database-1.cj4mmp0k4i3t.us-east-2.rds.amazonaws.com"
port = "5432"

# Construct the connection string
connection_string = f"dbname={dbname} user={user} password={password} host={host} port={port}"


def get_recommendations_by_id_handler(event, context):

    # setting up to handler
    id_value = int(event['pathParameters']['id'])

    connection = None
    cursor = None
    result_data = None

    try:
        # Establish a connection to the PostgreSQL database
        connection = psycopg2.connect(connection_string)
        print("Connected to the database!")

        # Create a cursor object to interact with the database
        cursor = connection.cursor()

        # Example: Execute a query using data from the Lambda event
        query = f"SELECT * FROM recommendations WHERE id={id}"
        # data = (event.get("value1"), event.get("value2"))
        # cursor.execute(query, data)
        cursor.execute(query)

        # Fetch all rows from the result set
        rows = cursor.fetchall()

        # Process the retrieved data
        result_data = []
        for row in rows:
            for i in range(1, len(row), 2):
                result_data.append(row[i])

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

    return result_data
