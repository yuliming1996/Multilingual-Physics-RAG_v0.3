def expand_query(
    rewritten,
):


    queries = [

        (
            f"rewritten_{rewritten.rewritten_query.type}",
            rewritten.rewritten_query.content,
        ),

        (
            f"translated_{rewritten.translated_query.type}",
            rewritten.translated_query.content,
        ),

        (
            "keyword_zh",
            rewritten.keywords.zh,
        ),

        (
            "keyword_en",
            rewritten.keywords.en,
        ),
    ]


    return queries