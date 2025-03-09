import re
from typing import List

from .base import QueryExpansionStrategy


class ParaphraseStrategy(QueryExpansionStrategy):
    """
    Generates multiple paraphrases of the given query.
    """

    def __init__(self, llm_manager, num_paraphrases: int = 3):
        self.llm_manager = llm_manager
        self.num_paraphrases = num_paraphrases

    def postprocess_response(self, response: str) -> List[str]:
        responses = response.split("\n")

        regex = re.compile(r"Paraphrase \d*:")
        responses = [r for r in responses if regex.match(r)]
        responses = [response[response.find('"') :] for response in responses]

        return responses[: self.num_paraphrases]

    def expand_query(self, query: str) -> List[str]:
        system_message = (
            "You are a helpful assistant specialized in MicroStep-MIS documentation. "
            "MicroStep-MIS develops and manufactures customized monitoring and information systems for environmental monitoring, "
            "including aviation, road weather, and marine systems. Please provide {self.num_paraphrases} distinct paraphrases of the user's query. "
            "Each paraphrase should preserve the core meaning while adding clarity and context relevant to MicroStep-MIS. "
            "Format your response as follows:\n\n"
            "Example:\n"
            'User query: "weather station"\n\n'
            'Paraphrase 1: "How do I set up my weather station?"\n'
            'Paraphrase 2: "What steps do I take to set up and calibrate my weather station?"\n'
            'Paraphrase 3: "How can I set my weather station in IMS?"\n\n'
            "Now, please generate the paraphrases for the given user query."
        )

        human_message = (
            f'User query: "{query}"\n'
            "Now, please generate paraphrases of the above query in the specified format:\n"
        )

        messages = [("system", system_message), ("human", human_message)]
        ai_msg = self.llm_manager.llm.invoke(messages)

        return self.postprocess_response(ai_msg.content)
