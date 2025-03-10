from llm import LLMManager
from query_expansion.compression_upscaling import CompressionUpscalingStrategy
from query_expansion.expansion_module import QueryExpansionModule
from query_expansion.paraphrase import ParaphraseStrategy


def main():
    llm_manager = LLMManager(model_name="llama3.2")

    # 1. Create a compression_upscaling strategy instance
    compression_strategy = CompressionUpscalingStrategy(
        llm_manager=llm_manager, min_words=10, max_words=50
    )
    expansion_module = QueryExpansionModule(strategy=compression_strategy)

    # 2. Use the expansion module to compress or upscale teh query
    long_user_query = """I'm interested in understanding the process of setting up a new satellite, but there are so many aspects to consider—launch logistics, orbital insertion, communication systems, power supply, and even regulatory approvals. Could you walk me through the major phases of getting a satellite from initial design to fully functional operation in space, highlighting the most critical challenges and considerations along the way?"""
    short_user_query = "How do I set up a satellite?"
    print(f"Long User Query:\n{long_user_query}\n")
    print(f"Short User Query:\n{short_user_query}\n")

    normalized_long_query = expansion_module.expand_query(long_user_query)
    print("Normalized Long Query:\n", normalized_long_query)

    normalized_short_query = expansion_module.expand_query(short_user_query)
    print("Normalized Short Query:\n", normalized_short_query)

    # 3. Switch to ParaphraseStrategy
    paraphrase_strategy = ParaphraseStrategy(llm_manager=llm_manager, num_paraphrases=3)
    expansion_module.set_strategy(paraphrase_strategy)

    # 4. Use the paraphrase strategy to generate multiple paraphrases of the normalized short query
    paraphrased_queries = expansion_module.expand_query(normalized_short_query)

    print("\nParaphrased Queries:")
    for paraphrase in paraphrased_queries:
        print(paraphrase)


if __name__ == "__main__":
    main()
