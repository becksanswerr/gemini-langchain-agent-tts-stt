from tavily import TavilyClient
client = TavilyClient("***REMOVED***")
response = client.search(
    query="elon musk"
)
print(response)