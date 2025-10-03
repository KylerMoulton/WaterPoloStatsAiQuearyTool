**config.json** should not be shared or committed. :)

**setup.sql** setups the database.

**db_bot.py** initializes the database, connects to openai, provides prompts and questions.

**strategies** attempting to try out the three strategies “zero-shot, single-domain, and cross-domain” as outlined in this paper: https://arxiv.org/abs/2305.11853 <- read it 😊

**responses_\<strategy>_\<time>.json** records the provided prompts and questions, as well as the generated SQL queries and responses.

**description** This database represents the mock data to manage an upcoming dogshow.

<a href="sample_post.md">**sample_post.md**</a> is a sample report of the data in this effort.

<a href="schema.png">schema.png</a> is a sample schema. Can you identify where foreign keys should exist but are not explicitly defined 😊? This was created from the sqlite database via <a href="https://www.google.com/search?q=install+schemacrawler">schemacrawler</a>:
```
schemacrawler --server sqlite --database .\aidb.sqlite --command=schema --output-file=./schema.png --info-level=standard
```


