from .base import QueryExpansionStrategy


class CompressionUpscalingStrategy(QueryExpansionStrategy):
    """
    If the query is too long, compress it.
    If the query is too short, expand it.
    Otherwise, return as is.
    """

    def __init__(
        self,
        llm_manager,
        min_words: int = 10,
        max_words: int = 50,
    ):
        self.llm_manager = llm_manager
        self.min_words = min_words
        self.max_words = max_words

    @staticmethod
    def postprocess_response(response: str) -> str:
        response_split = response.split("\n\n")

        if len(response_split) == 1:
            first_double_quotation_mark = response.find('"')
            if first_double_quotation_mark == -1:
                return response
            return response[first_double_quotation_mark:]

        responses = [r for r in response_split if r.startswith('"') and r.endswith('"')]
        if not responses:
            first_double_quotation_mark = response_split[0].find('"')
            return response_split[0][first_double_quotation_mark:]

        return " ".join(responses)

    def expand_query(self, query: str) -> str:
        query_length = len(query.split())

        if query_length < self.min_words:
            messages = [
                (
                    "system",
                    "You are a helpful assistant specialized in MicroStep-MIS documentation. "
                    "MicroStep-MIS develops and manufactures customized monitoring and information systems for environmental monitoring, "
                    "including aviation, road weather, and marine systems. The user's query is too short! "
                    "Please expand or elaborate on it so that it becomes more descriptive and contextual. "
                    "For example, if the original query is 'calibration', you might expand it to 'What are the detailed steps and best practices "
                    "for calibrating a MicroStep-MIS automated weather station for environmental monitoring?'",
                ),
                (
                    "human",
                    f'User query: "{query}"'
                    "Now, please expand this query into 1 full sentence. "
                    "Single expanded query:\n",
                ),
            ]
            ai_msg = self.llm_manager.llm.invoke(messages)
            return self.postprocess_response(ai_msg.content)

        elif query_length > self.max_words:
            messages = [
                (
                    "system",
                    "You are a helpful assistant specialized in MicroStep-MIS documentation. "
                    "MicroStep-MIS is known for its advanced monitoring and information systems used in environmental monitoring. "
                    "The user's query is too long! Please compress or summarize it while preserving its core meaning and ensuring the summary "
                    "aligns with the context of MicroStep-MIS documentation. "
                    "For example, if the query is 'What are the comprehensive steps, detailed procedures, and technical specifications involved in "
                    "calibrating, installing, and maintaining an automated weather station developed by MicroStep-MIS?', you might compress it to "
                    "'What are the key procedures for calibrating a MicroStep-MIS weather station?'",
                ),
                (
                    "human",
                    f'User query: "{query}"'
                    "Now, please summarize this query into 1-2 sentences. "
                    "Single shortened query:\n",
                ),
            ]
            ai_msg = self.llm_manager.llm.invoke(messages)
            return self.postprocess_response(ai_msg.content)

        else:
            # Return the query as is if it falls within the threshold.
            return query
