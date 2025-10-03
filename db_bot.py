import json
from openai import OpenAI
import os
import sqlite3
from time import time

print("Running db_bot.py for Utah Club Water Polo!")

# File paths
fdir = os.path.dirname(__file__)
def getPath(fname):
    return os.path.join(fdir, fname)

sqliteDbPath = getPath("aidb.sqlite")
setupSqlPath = getPath("setup.sql")
setupSqlDataPath = getPath("setupData.sql")

# Remove old database
if os.path.exists(sqliteDbPath):
    os.remove(sqliteDbPath)

# Connect to SQLite
sqliteCon = sqlite3.connect(sqliteDbPath)
sqliteCursor = sqliteCon.cursor()

# Load schema and seed data
with open(setupSqlPath) as f:
    setupSqlScript = f.read()
with open(setupSqlDataPath) as f:
    setupSqlDataScript = f.read()

sqliteCursor.executescript(setupSqlScript)
sqliteCursor.executescript(setupSqlDataScript)

def runSql(query):
    """Run a single SQL statement and return results, handling errors."""
    try:
        result = sqliteCursor.execute(query).fetchall()
        sqliteCon.commit()
        return result
    except Exception as e:
        print(f"SQL Error: {e}")
        return None  # Return None on error instead of empty list

# OpenAI setup
configPath = getPath("config.json")
with open(configPath) as f:
    config = json.load(f)

openAiClient = OpenAI(api_key=config["openaiKey"])
openAiClient.models.list()  # validate key

def getChatGptResponse(content):
    """Get GPT response in streaming mode."""
    stream = openAiClient.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": content}],
        stream=True,
    )
    response = []
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            response.append(chunk.choices[0].delta.content)
    return "".join(response)

def sanitizeForJustSql(value):
    """Extract the SQL code from GPT response, remove garbage lines."""
    gptStartSqlMarker = "```sql"
    gptEndSqlMarker = "```"
    if gptStartSqlMarker in value:
        value = value.split(gptStartSqlMarker)[1]
    if gptEndSqlMarker in value:
        value = value.split(gptEndSqlMarker)[0]
    # Remove lines that are empty or comment-only
    lines = value.splitlines()
    lines = [line for line in lines if line.strip() and not line.strip().startswith('--')]
    return "\n".join(lines).strip()

# Strategies: now water polo oriented
commonSqlOnlyRequest = (
    " Give me a sqlite select statement that answers the question. "
    "Only respond with sqlite syntax. Do not combine multiple statements! "
    "Do not explain errors."
)

strategies = {
    "zero_shot": setupSqlScript + commonSqlOnlyRequest,
    "team_data_shot": (
        setupSqlScript +
        " Who are the top 5 scorers this season? Include goals, assists, and total shots. " +
        commonSqlOnlyRequest
    ),
    "match_analysis_shot": (
        setupSqlScript +
        " Analyze the current season's matches. List the top 5 highest scoring matches and biggest margins of victory. " +
        commonSqlOnlyRequest
    ),
    "player_stats_shot": (
        setupSqlScript +
        " Provide player-specific stats for the season. Limit to top 5 for goals, assists, steals, blocks, and exclusions. " +
        commonSqlOnlyRequest
    )
}

# Water polo top-5 questions
questions = [
    "Which teams have the most wins this season (top 5)?",
    "Who are the top 5 scorers across all teams?",
    "Which 5 matches had the largest winning margins?",
    "Which 5 referees officiated the most matches?"
]

# Run strategies and queries
for strategy_name, strategy_prefix in strategies.items():
    responses = {"strategy": strategy_name, "prompt_prefix": strategy_prefix}
    questionResults = []

    print("#" * 80)
    print(f"Running strategy: {strategy_name}")

    for question in questions:
        print("~" * 80)
        print(f"Question: {question}")

        sqlSyntaxResponse = ""
        queryRawResponse = ""
        friendlyResponse = ""
        error = None

        try:
            # Get GPT SQL
            prompt = strategy_prefix + " " + question
            sqlSyntaxResponse = getChatGptResponse(prompt)
            sqlSyntaxResponse = sanitizeForJustSql(sqlSyntaxResponse)
            print("SQL Syntax Response:")
            print(sqlSyntaxResponse)

            # Run SQL if it exists
            if sqlSyntaxResponse:
                result = runSql(sqlSyntaxResponse)
                if result is None:
                    queryRawResponse = "SQL Error occurred"
                    friendlyResponse = f"Could not retrieve data for: {question}"
                elif result == []:
                    queryRawResponse = "[]"
                    friendlyResponse = f"No data found for: {question}"
                else:
                    queryRawResponse = str(result)
                    friendlyPrompt = (
                        f"I asked: '{question}' and the query returned: '{queryRawResponse}'. "
                        "Please provide a concise, friendly answer without extra chatter."
                    )
                    friendlyResponse = getChatGptResponse(friendlyPrompt)
            else:
                queryRawResponse = "No SQL generated"
                friendlyResponse = f"GPT did not generate SQL for: {question}"

        except Exception as e:
            error = str(e)
            print(f"Error: {error}")
            queryRawResponse = "Exception"
            friendlyResponse = f"Error occurred: {error}"

        questionResults.append({
            "question": question,
            "sql": sqlSyntaxResponse,
            "queryRawResponse": queryRawResponse,
            "friendlyResponse": friendlyResponse,
            "error": error
        })

    responses["questionResults"] = questionResults

    # Save response JSON
    filename = f"response_{strategy_name}_{int(time())}.json"
    with open(getPath(filename), "w") as f:
        json.dump(responses, f, indent=2)

sqliteCursor.close()
sqliteCon.close()
print("Done!")
