from tavily import TavilyClient
client = TavilyClient("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")
response = client.search(
    query="elon musk"
)
print(response)