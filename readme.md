# Sakila Database Query Tool

This tool is designed to interact with the Sakila database, allowing users to perform complex queries and retrieve information in a user-friendly format. The tool uses a combination of SQL queries and language models to interpret user prompts, execute the appropriate queries, and return the results.

## Features

- **get_system_instructions**: This function provides the database schema to help generate SQL statements.

- **get_movie_synopsis**: This function searches for a movie synopsis using Google Search and a language model.

- **verify_sql_with_prompt**: This function verifies a given SQL statement against a user prompt using a language model.

- **execute_sql**: This function executes SQL queries against the database.

- **Workflow**: The tool includes a workflow that uses the above functions to interpret user prompts, execute the appropriate queries, and return the results.

## Usage

To use the tool, provide a user prompt in the form of a question about the Sakila database. The tool will interpret the prompt, execute the appropriate queries, and return the results.

## Configuration

The tool requires access to the Sakila database and the Google Search API. It also requires the OpenAI language model.

## Database Schema

The tool uses the following database schema to interpret user prompts and execute queries:

- sakila.actor
- address
- category
- city
- country
- customer
- film
- film_actor
- film_category
- inventory
- language
- payment
- rental
- staff
- store

Each table includes various fields that can be used in queries. For more information about the schema, refer to the `schema.txt` file.

