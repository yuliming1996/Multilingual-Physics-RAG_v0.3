from openai import OpenAI
from pydantic import BaseModel
import os
import json
from app.config import (
    QUERY_REWRITE_MODEL,
    REWRITE_API_BASE,
    REWRITE_API_KEY,
)

client = OpenAI(
    api_key=os.environ[REWRITE_API_KEY],
    base_url=REWRITE_API_BASE,
)

class KeywordQuery(BaseModel):

    zh: str

    en: str

class QueryItem(BaseModel):

    content: str

    type: str
class QueryRewrite(BaseModel):
    rewritten_query: QueryItem

    translated_query: QueryItem

    keywords: KeywordQuery


def rewrite_query(
    query: str,
):


    response = client.chat.completions.create(

        model=QUERY_REWRITE_MODEL,


        messages=[

            {
                "role": "system",

                "content":
                """
You are a physics retrieval query rewriting assistant.

Your task is NOT to answer the physics question.

Your task is to transform the user's question into
high-quality retrieval queries for a bilingual
Chinese-English physics knowledge base.


Requirements:

1. Analyze the physics intent behind the user's question.

2. Rewrite the question into a clearer and more professional
physics query.

- Preserve the original language.
- Add missing technical context when helpful.
- Do not introduce unrelated concepts.

3. Translate the rewritten query into the other language
(Chinese ↔ English) using standard physics terminology.
If the rewritten query is Chinese, translate it into English.
If the rewritten query is English, translate it into Chinese.
The purpose of translation is to retrieve knowledge
from the other language part of the bilingual physics corpus.

4. Generate concise bilingual keyword queries.

Generate:
(1). Chinese keywords for Chinese documents.
(2). English keywords for English documents.

Use standard physics terminology.

Return ONLY JSON:

{
    "rewritten_query": {
        "content": "",
        "type": "zh or en"
    },

    "translated_query": {
        "content": "",
        "type": "zh or en"
    },

    "keywords": {
        "zh": "",
        "en": ""
    }
}


Rules:

- rewritten_query.type must indicate the language
  of rewritten_query.content.

- translated_query.type must indicate the language
  of translated_query.content.

- keywords must contain both Chinese and English keyword queries.

- keywords.zh should contain Chinese physics terminology.

- keywords.en should contain standard English physics terminology.
"""
            },


            {
                "role": "user",
                "content": query,
            }

        ],


        response_format={
            "type": "json_object"
        }
    )



    content = (
        response
        .choices[0]
        .message
        .content
    )


    if content is None:

        raise ValueError(
            "rewrite_query: No content returned from the API"
        )


    data = json.loads(
        content
    )


    return QueryRewrite(
        rewritten_query=QueryItem(**data["rewritten_query"]),
        translated_query=QueryItem(**data["translated_query"]),
        keywords=KeywordQuery(**data["keywords"]),
    )