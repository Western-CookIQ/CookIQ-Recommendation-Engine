from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import CohereEmbeddings
from langchain.prompts import PromptTemplate
from langchain_community.llms import Cohere
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import LLMChain
import os
import psycopg2
# import requests
import json
# import boto3


os.environ["COHERE_API_KEY"] = "4m1kzTf4OQmGP5sqbpAjKWFL4S0ohgJgqPvbU8qC"
embeddings = CohereEmbeddings(model="embed-english-light-v3.0")

# s3_bucket = 'cookiq-llm2'
# model_key = 'final.txt'
# s3 = boto3.resource('s3')


# def get_titles():
#     return requests.get(
#         "https://cookiq-llm2.s3.us-east-2.amazonaws.com/final.txt"
#     )


def create_db():
    loader = TextLoader('./titles.txt')
    transcript = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=64, chunk_overlap=0)
    docs = text_splitter.split_documents(transcript)

    db = FAISS.from_documents(docs, embeddings)
    return db


def get_recipe_info(name):
    host = "database-1.cj4mmp0k4i3t.us-east-2.rds.amazonaws.com"
    port = "5432"
    database = "initial_db"
    user = "postgres"
    password = "cookiq123"

    try:
        conn = psycopg2.connect(
            dbname=database, user=user, password=password, host=host, port=port
        )

        cursor = conn.cursor()

        cursor.execute(f"SELECT * FROM recipe WHERE name = '{name}';")

        rows = cursor.fetchall()

        cursor.close()
        conn.close()

        return rows[0]

    except psycopg2.Error as e:
        print("Error connecting to the database:", e)


def format_recipe(response):
    return f"The recipe '{response[1]}' is described as '{response[2]}'. It consists of {response[3]} steps and takes {response[4]} minutes to prepare. The steps involved are: {response[5]}."


def get_response_from_query(question, recipe):
    llm = Cohere()

    prompt = PromptTemplate(
        input_variables=["question", "recipe"],
        template="""
        You are a helpful assistant that that can answer questions about food from the given information.

        Answer the following question: {question}
        According to the following recipe information: {recipe}

        Only use the factual information from the recipe to answer the question.

        If you feel like you don't have enough information to answer the question, say "I don't know".
        """,
    )

    chain = LLMChain(llm=llm, prompt=prompt)

    response = chain.run(question=question, recipe=recipe)
    response = response.replace("\n", "")
    return response


def lambda_handler(event, context):
    query = event["queryStringParameters"]["query"]

    db = create_db()
    search_result = db.similarity_search(query)
    recipe = search_result[0].page_content.split(";")[0].strip()
    recipe_info = get_recipe_info(recipe)
    formatted_recipe = format_recipe(recipe_info)
    response = get_response_from_query(query, formatted_recipe)

    res_body = {
        # "query": query,
        # "recipe": recipe,
        # "recipe_info": recipe_info,
        # "formatted_recipe": formatted_recipe,
        "response": response,
    }

    http_response = {
        "statusCode": 200,
       'headers': {
            "Content-Type": 'application/json',
            "Access-Control-Allow-Headers": 'Content-Type,X-Amz- Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            "Access-Control-Allow-Methods": 'OPTIONS,GET',
            "Access-Control-Allow-Credentials": True,
            "Access-Control-Allow-Origin": '*',
            "X-Requested-With": '*'
        },
        "body": json.dumps(res_body),
    }
    return http_response
