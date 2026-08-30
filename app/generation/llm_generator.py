import os

from openai import OpenAI

from app.config import (
    GENERATION_MODEL,
    GENERATION_API_BASE,
    ANSWER_LANGUAGE,
    GENERATION_API_KEY,
)


client = OpenAI(
    api_key=os.environ[GENERATION_API_KEY],
    base_url=GENERATION_API_BASE,
)


def generate_answer(
    original_query: str,
    rewritten_query: str,
    context: str,
):


    response = client.chat.completions.create(

        model=GENERATION_MODEL,

        messages=[
            {
                "role": "system",

                "content":
                f"""
You are a physics knowledge assistant.

Your task is to answer the user's physics question
using the retrieved context.

Rules:

1. Use the retrieved documents as the primary knowledge source.

2. Answer the physical question itself rather than merely
   summarizing the retrieved documents.

3. Synthesize information from multiple retrieved documents
   when they provide complementary explanations.

4. Prioritize the underlying physical principles and conceptual
   relationships over superficial descriptions or isolated examples.

5. Use standard physics terminology and equations when helpful.

6. Do not introduce claims that conflict with the retrieved context.

7. If the retrieved context does not contain enough information
   to answer the question reliably, explicitly state the limitation.

8. The rewritten query is a clarified representation of the user's
   intent. Use it to understand the intended physics question,
   but make sure the final answer still addresses the original query.

Output language:

Generate the final answer in {ANSWER_LANGUAGE}.

Do not change the output language based on the language of the
question or retrieved documents.
"""
            },

            {
                "role": "user",

                "content":
                f"""
Original question:
{original_query}

Rewritten question:
{rewritten_query}

Retrieved context:
{context}
"""
            },
        ],
    )


    content = (
        response
        .choices[0]
        .message
        .content
    )


    if content is None:

        raise ValueError(
            "LLM answer content is empty"
        )


    return content