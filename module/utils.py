# pylint: disable = C0301
"""
Utility functions.
"""

import os
import re
import logging

from dotenv import load_dotenv
import httpx


# from bs4 import BeautifulSoup
# import readability
import trafilatura

from docs_list import docs_urls


load_dotenv()
google_api_key = os.getenv("GOOGLE_API_KEY")
google_cx = os.getenv("Search_Engine_ID")


def remove_emojis(text: str) -> str:
    """
    Remove emojis from the given text.
    """
    emoji_pattern = re.compile(
        "["
        "\U0001f300-\U0001f5ff"  # symbols & pictographs
        "\U0001f600-\U0001f64f"  # emoticons
        "\U0001f680-\U0001f6ff"  # transport & map
        "\U0001f1e0-\U0001f1ff"  # flags
        "\U0001f900-\U0001f9ff"  # supplemental symbols & pictographs ▶ newly added
        "\u2600-\u26ff"  # misc symbols
        "\u2700-\u27bf"  # dingbats
        "\ufe00-\ufe0f"  # variation selectors
        "]+",
        flags=re.UNICODE,
    )
    return emoji_pattern.sub(r"", text).strip()


async def google_search(query: str) -> list | None:
    """
    Search source links using Google Custom Search API.
    """
    search_results = []
    search_url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={google_api_key}&cx={google_cx}"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(search_url, timeout=30)
            response.raise_for_status()
            results = response.json()
            for item in results["items"][:7]:
                title = remove_emojis(item["title"])
                search_results.append(
                    {"query": query, "title": title, "url": item["link"]}
                )
        except httpx.TimeoutException:
            logging.error("Search timeout error")
            return None
        except httpx.HTTPError as e:
            logging.error("HTTP error: %s", e)
            return None
        except ValueError as e:
            logging.error("Error decoding JSON: %s", e)
            return None

    # print(f"\nExtracted URL : {search_results}")
    return search_results


async def get_contents(item: dict) -> dict | None:
    """
    Fetch the text content from the given URL.
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(item["url"], timeout=30)

            # readability library outputs not good in some cases(langchain documentations).
            # dummy_soup = BeautifulSoup(response.content, "html.parser")
            # dummy_text = dummy_soup.get_text(separator="\n", strip=True)

            # main_html = readability.Document(response.text).summary()
            # soup = BeautifulSoup(main_html, "html.parser")
            # raw_text = soup.get_text(separator="\n", strip=True)

            # trafilatura seems best in most cases
            extracted_content = trafilatura.extract(
                response.text, include_comments=False
            )
            lines = [
                line.strip() for line in extracted_content.splitlines() if line.strip()
            ]
            cleaned = "\n".join(lines)
            cleaned = remove_emojis(cleaned)

            # Log for debugging

            # print(f"Cleaned text from {item['url']}: {cleaned}")
            item["text"] = cleaned
        except httpx.TimeoutException:
            logging.error("Fetch url timeout error")
            return None
        except httpx.RequestError as e:
            logging.error("Fetch url error : %s", e)
            return None
        except httpx.HTTPError as e:
            logging.error("HTTP error: %s", e)
            return None

    return item


def build_docstring() -> str:
    """
    Dynamically script the docstring for the mcp server.
    """
    doc_names_list = [*docs_urls]
    doc_names_string = ""
    for _ in doc_names_list[:-1]:
        doc_names_string += _ + ", "
    doc_names_string = doc_names_string[:-1] + " and " + doc_names_list[-1]
    return f"""
        Search the latest docs for a given query and library.
        Support {doc_names_string}.

        Args:
            query : The query to search for (e.g. "DynamoDB"). Must be in English. If not, translate it to English. When applicable, combine the user's question with the relevant programming language to enhance search accuracy.
            library : The library to search in (e.g. "aws", "next.js"). Must be in English. If not, translate it to English.
        Returns:
            A single string representing a list of found documents or an error message.
        """
