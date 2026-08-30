from pathlib import Path

from app.retrieval.schema import RetrievalCandidate


def get_source_title(
    metadata: dict,
):

    title = metadata.get(
        "title"
    )


    if title:

        return title


    file_name = metadata.get(
        "file_name"
    )


    if file_name:

        return file_name


    relative_path = metadata.get(
        "relative_path"
    )


    if relative_path:

        return Path(
            relative_path
        ).stem


    source = metadata.get(
        "source"
    )


    if source:

        return Path(
            source
        ).stem


    return "Untitled source"



def build_context(
    candidates: list[RetrievalCandidate],
    max_documents: int = 5,
):

    contexts = []


    for i, candidate in enumerate(
        candidates[:max_documents],
        start=1,
    ):


        metadata = candidate.chunk.get(
            "metadata",
            {}
        )


        title = get_source_title(
            metadata
        )


        language = metadata.get(
            "language",
            ""
        )


        content = candidate.chunk.get(
            "page_content",
            ""
        )


        contexts.append(
            f"""
            [Document {i}]
            Language:
            {language}

            Title:
            {title}

            Content:
            {content}
            """
                    )


    return "\n\n".join(
        contexts
    )