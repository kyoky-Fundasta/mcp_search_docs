# pylint: disable = C0301
"""
Module to evaluate the relevancy of the reference documents to the query.
This code is scripted for free tier Gemini account.
You may use async version of code with paid API service.
"""

import os

# import time
import asyncio
import json
import logging

from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai import errors as google_errors


load_dotenv()
gemini_api_key = os.getenv("Gemini_API_KEY")


async def gemini_client(input_item: dict) -> dict:
    """
    Check the given text relevant to the query.

    input_item format : {"query":query, "title":title, "url":url, "text":text}
    """
    client = genai.Client(
        api_key=gemini_api_key,
    )
    async_client = client.aio
    model = "gemini-2.0-flash"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(
                    text=f"""
                                     -title: {input_item["title"]}
                                     -query: {input_item["query"]}
                                     -text: {input_item["text"]}
                                     """
                ),
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        temperature=0,
        top_p=0.5,
        response_mime_type="application/json",
        system_instruction=[
            types.Part.from_text(
                text="""
                **### **System Prompt: Relevance-Based Text Trimmer**

Your task is to **trim a source text** and then evaluate the **trimmed text's relevance to a given query**. 
You **must not modify, rewrite, or paraphrase** the original content—your job is to **remove** parts that are clearly unnecessary or distracting.

---

### **Input format**:
- `title`: The title of the original documentation  
- `query`: The user's question  
- `text`: A source text collected from the documentation  

---

### **Instructions**:

1. **Understand the Query**: Carefully read the `query` to understand the user's intent.

2. **Assess the Text with Respect to the Title**:  
   - Use the `title` to identify and filter out **distracting or off-topic content**, such as UI labels, cookie messages, unrelated ads, or survey prompts.
   - Retain content that is **related to the title** or that may be **helpful for answering the query**, even if it doesn't relate to the title.

3. **Trim the Text Conservatively**:  
   - Remove only the content that is **not relevant to the title** *and* does **not help answer the query**.
   - Preserve any information that may be **indirectly useful** or necessary to understand relevant parts.

4. **Evaluate Relevance**:  
   - Assess the **relevance of the trimmed text** solely with respect to the `query`, **not the title**.
   - Assign a **relevance score** between `0` and `100`, where:
     - `100` = the trimmed text is both necessary and sufficient to answer the query, with no extra details.
     - `0` = the trimmed text is **completely irrelevant** and has **no potential** to help answer the query
     - Intermediate scores reflect how much additional context is needed—deduct points proportionally for missing relevant information or for extraneous content.
---

### **Output format (JSON)**:
```json
{
  "text": "Trimmed source text as a single continuous string.",
  "score": "Relevance score as a string from 0 to 100.",
  "comment": "Brief explanation of how the trimmed content may help answer the query."
}
```

---

### Notes:
- Do **not rewrite, paraphrase, or add explanations** to the text—**only trim**. But you may describe your thought in the "comment" field.
- Do **not** include any extra output beyond the JSON result.



### Let's begin:
"""
            ),
        ],
    )

    response = await async_client.models.generate_content(
        model=model,
        contents=contents,
        config=generate_content_config,
    )

    # print("\nTime:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    # print("Total Token size:", response.usage_metadata.total_token_count, "\n")

    output = json.loads(response.text)

    output["url"] = input_item["url"]
    output["query"] = input_item["query"]
    output["title"] = input_item["title"]
    return output


async def check_docs(input_list: list) -> list:
    """
    Asynchronous checking process.

    input_list format : [{"query":query, "title":title, "url":url, "text":text} ... ]
    """

    # Free tier's maximum number of concurrent API call is 3
    tasks = [gemini_client(item) for item in input_list]

    try:
        responses = await asyncio.gather(*tasks)
    except google_errors.ClientError as e:
        if e.response.status_code == 429:
            logging.error("\nError in the check_doc phase: %s", e)
            for detail in e.details["error"]["details"]:
                if detail.get("@type") == "type.googleapis.com/google.rpc.RetryInfo":
                    interval = detail["retryDelay"]
                    return f"429 errored in the data processing. necessary interval: {interval}"
        else:
            logging.error("\nError in the check_doc phase: %s", e)
            return "errored in the data processing"

    # Remove unrelated content
    if isinstance(responses, list) and responses:
        responses = [item for item in responses if int(item["score"]) != 0]
        return sorted(responses, key=lambda x: int(x["score"]), reverse=True)
    else:
        return input_list


if __name__ == "__main__":
    from test_data import dict_1, dict_2, dict_3

    for i in [dict_1, dict_2, dict_3]:
        pass
        # print(asyncio.run(gemini_client(i)))
