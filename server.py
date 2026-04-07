from fastmcp import FastMCP
import requests

# INITIALIZATION: Setting up the MCP Server and the API Connector
my_bot = FastMCP("Reactome_Bot")

@my_bot.tool()
def search_reactome(gene_symbol):
    my_url = "https://reactome.org/ContentService/search/query"

    # PARAMETER CONFIGURATION: Defining the search query for the API
    my_params = {
        "query": str(gene_symbol),
        "cluster": "true"
    }
    
    try:

        # RETRIEVAL: Fetching external data from a REST API
        my_response = requests.get(my_url, params=my_params, timeout=10)
        
        if my_response.status_code == 200:
            # DATA PARSING: Converting raw JSON response into a Python dictionary
            my_data = my_response.json()
            my_results = my_data.get("results", [])
            
            # VALIDATION: Handling cases where no data exists for the input
            if len(my_results) == 0:
                return "I could not find any pathways for: " + str(gene_symbol)
            
            my_output = "Reactome Results for " + str(gene_symbol) + ":\n\n"
            
            # AUGMENTATION: Iterating through structured data to build a high-signal context
            for group in my_results:
                group_name = group.get("typeName", "Other")
                entries = group.get("entries", [])
                
                if len(entries) > 0:
                    my_output = my_output + "Category: " + str(group_name) + "\n"
                    
                    # DATA FILTERING: Limiting results to the Top 3 to prevent LLM context clutter
                    count = 0
                    for item in entries:
                        if count < 3:
                            name = item.get("name", "No Name")
                            id_num = item.get("stId", "")
                            
                            my_output = my_output + "  - " + str(name)
                            if id_num != "":
                                my_output = my_output + " (ID: " + str(id_num) + ")"
                            my_output = my_output + "\n"
                            
                            count = count + 1
                    
                    my_output = my_output + "\n"
            
            # GENERATION STEP: Returning the grounded data to the LLM for final response
            return my_output
            
        else:
            # EXCEPTION HANDLING: Capturing API-side errors (e.g., 404, 500)
            return "The website gave an error. Code: " + str(my_response.status_code)
            
    except Exception as error:
        # NETWORK RESILIENCE: Catching connection timeouts or DNS failures
        return "Connection Error: " + str(error)

if __name__ == "__main__":
    # DEPLOYMENT: Starting the MCP server to listen for AI requests
    my_bot.run()
