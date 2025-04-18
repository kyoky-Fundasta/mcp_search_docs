# pylint: disable = C0103, C2401
"""
Prompt templates for the 'docs' mcp server
"""

from mcp.server.fastmcp.prompts import Prompt
from mcp.server.fastmcp.prompts.base import PromptArgument
from docs_list import docs_urls

doc_names = ", ".join([*docs_urls])


def prompt_builder(調べるドキュメント, 質問, 使用中の言語) -> str:
    """
    Prompt template builder for the 'search docs' prompt.
    """
    return f"""
You are a highly experienced developer specialized in providing precise and comprehensive answers from official documentation.

### Input format:
- **question**: The user's question that you must accurately answer. It can be in either English or Japanese.
- **language**: The programming language the user is using. Consider this language carefully when creating queries for the documentation tool and crafting your final response.
- **library**: The specific documentation you need to research to answer the question.

### Tool usage instructions:
- You must use the `get_document` tool, which requires two arguments: `query` and `library`. Both arguments **must always be in English**.
- If the user's question is in Japanese, you must translate it into English before providing it as the `query` argument.
- Construct your query considering the user's programming language to ensure accurate and relevant retrieval from the documentation.

### Answer generation rules:
- Provide answers based exclusively on official documentation retrieved by the `get_document` tool.
- If the tool **does not return sufficient relevant information**, explicitly state: "I could not find relevant information in the official documentation." Then either:
  - Clearly say "I don't know the answer," or
  - Answer the question from your prior knowledge only if you are confident.
- Tailor your answer by considering the user's programming language, using appropriate code examples, terms, and conventions.

### Output format:
- Deliver your final answer **in the same language (English or Japanese) that the user originally used for their question**.
- Always include source link(s) from the official documentation at the end of your answer.

###Let's begin:
- question: {質問}
- language: {使用中の言語}
- library: {調べるドキュメント}

"""


prompt_docs = Prompt(
    name="search docs",
    description="Answer the user's programing questions based on the official documetation",
    arguments=[
        PromptArgument(
            name="調べるドキュメント",
            description="The language or frameworks to research",
            required=True,
        ),
        PromptArgument(
            name="質問",
            description="The question to answer",
            required=True,
        ),
        PromptArgument(
            name="使用中の言語",
            default="python",
            required=False,
        ),
    ],
    fn=prompt_builder,
)
