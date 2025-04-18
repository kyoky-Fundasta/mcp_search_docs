# pylint: disable = C0301, C0103, W0104, C0116, C2401, W0718
"""
A custom mcp tool to check the latest documents on the web.
"""

import asyncio
import logging
import json

from mcp.server.fastmcp import FastMCP

from docs_list import docs_urls
from prompts import prompt_docs

from module.checking_doc import check_docs
from module.utils import google_search, get_contents, build_docstring

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

mcp = FastMCP("docs")

USER_AGENT = "docs-app/1.0"


@mcp.resource("mcp:/support/documentation/list")
def registed_languages_list() -> str:
    """
    To get the supported official documentation languages.
    """
    return "Answer the user the following available documentation list: " + ", ".join(
        [*docs_urls]
    )


async def get_document(query: str, library: str) -> str:
    if library not in docs_urls:
        return (
            "No documentation found. Currently, {library} is not available in our list."
        )
    query = f"site:{docs_urls[library]} -filetype:pdf {query}"
    final_answer = ""

    # shape of fetched_urls(list) : [{"query":query,"title":title, "url":url} ... ]
    fetched_urls = await google_search(query)
    logging.info("Google search result: %s", fetched_urls)
    if isinstance(fetched_urls, list) and fetched_urls:

        # shape of fetched_texts(list) : [{"query":query, "title":title, "url":url, "text":text} ... ]
        fetched_texts = await asyncio.gather(
            *[get_contents(url_dict) for url_dict in fetched_urls]
        )
        fetched_texts = [item for item in fetched_texts if item and item.get("text")]
        if fetched_texts:
            try:
                texts_with_scores = await check_docs(fetched_texts)
                if (
                    int(texts_with_scores[0]["score"]) >= 95
                    and int(
                        texts_with_scores[1]["score"] + texts_with_scores[2]["score"]
                    )
                    >= 160
                ):
                    texts_with_scores = texts_with_scores[:3]
                elif (
                    int(texts_with_scores[0]["score"]) >= 80
                    and int(
                        texts_with_scores[1]["score"] + texts_with_scores[4]["score"]
                    )
                    >= 250
                ):
                    texts_with_scores = texts_with_scores[:5]

                logging.info("### No of selected documents: %d", len(texts_with_scores))

                for i, d in enumerate(texts_with_scores):
                    final_answer += f'\n----------\n\n###text_no: {i+1}\n###title: {d.get("title", "N/A")}\n###source_link: {d.get("url", "N/A")}\n###relevancy_score: {d.get("score", "N/A")}\n###comment: {d.get("comment", "N/A")}\n###text: {d.get("text", "")}'
                    logging.info("Final output: %s", final_answer)
                    # print("Final output:", final_answer)
                    # text_results.append(
                    #     {
                    #         "text_no": i + 1,
                    #         # Use .get() for safer access in case keys are missing
                    #         "title": d.get("title", "N/A"),
                    #         "source_link": d.get("url", "N/A"),
                    #         "relevancy_score": d.get("score", "N/A"),
                    #         "comment": d.get("comment", "N/A"),
                    #         "text": d.get("text", ""),
                    #     }
                    # )
            # --- Catching the JSON Decode Error ---
            except json.JSONDecodeError as e:
                # Log the specific JSON error details
                logging.error("JSONDecodeError occurred: %s", e.msg)
                logging.error(
                    "Error occurred at line %d, column %d (char %d)",
                    e.lineno,
                    e.colno,
                    e.pos,
                )
                # *** Log the problematic data ***
                # This assumes 'texts_with_scores' holds the string that failed parsing.
                # If parsing happens inside check_docs, you'll need to modify check_docs
                # to log its input upon failure.
                logging.error(
                    "Data that caused JSON error (if available from check_docs): %s",
                    texts_with_scores,
                )
                # Return a specific error message to the client
                return f"Error executing tool get_document: Internal data parsing failed (JSONDecodeError: {e.msg} at pos {e.pos})."
            # --- Catching other potential errors during check_docs/processing ---
            except Exception as e:
                logging.error(
                    "An unexpected error occurred during/after check_docs: %s",
                    e,
                    exc_info=True,
                )
                logging.error(
                    "Data state during error: fetched_texts count=%d, texts_with_scores=%s",
                    len(fetched_texts),
                    texts_with_scores,
                )
                return f"Error executing tool get_document: An unexpected error occurred ({type(e).__name__})."

        else:
            return "No relevant information found in the documentation."

    else:
        logging.error("URL output is not a list : %s", fetched_urls)
    # return json.dumps(text_results, ensure_ascii=False, indent=2)
    return final_answer


# Dynamically script and add the docscring(instruction for the mcp server) to the mcp server function
# get_document.__doc__ = build_docstring()

# Manually register the function with MCP
mcp.add_tool(get_document, description=build_docstring())
mcp.add_prompt(prompt_docs)


if __name__ == "__main__":
    mcp.run(transport="stdio")

    # from test_data import dummy_query

    # asyncio.run(get_document(dummy_query, "langchain"))
    # # asyncio.run(
    # #     google_search(
    # #         "how can I initiate a new next.js project using aws amplify"
    # #     )
    # # )
