import re
import logging
import requests
import pandas as pd
from bs4 import BeautifulSoup

URL = "https://www.worldometers.info/world-population/population-by-country/"
headers = {"User-Agent": "ali/2021.44.30.15-b917dc"}
output_file_name = 'world_population.csv'

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Setting from least severity level
    format='Date-Time : %(asctime)s : Line No : %(lineno)d - %(message)s : Func Name : %(funcName)s : Level Name : %(levelname)s : Level No : %(levelno)s'
)

# Define the scraper function
def scraper():
    """
    The function fetches HTML content from the provided URL, extracts and cleans table data, and stores it
    into a CSV file. The process also includes error handling for different scenarios such as connection issues,
    request timeouts, and unexpected errors. The function returns a result dictionary.

    Returns:
        dict: A dictionary with the following keys:
            - success (int): 1 if the scraping is successful, 0 otherwise.
            - data (dict): An empty dictionary (placeholder for future enhancements).
            - message (str): A success or error message describing the result of the scraping.
            - error_code (str): A code representing the type of error (if any). Possible values:
    
    Sample Input:
        URL = "https://www.worldometers.info/world-population/population-by-country/"
        headers = {"User-Agent": "xyz/2021.44.30.15-b917dc"}

    Sample Output:
        Result dictionary:
        {
            "success": 1,
            "data": {},
            "message": "Scraping completed and data saved to 'world_population.csv'",
            "error_code": "0"
        }
    """
    logging.debug("Entering scraper function")
    result = {"success" : 0, "data": {}, "message" : "", "error_code": "0"}

    try:
        html = requests.get(URL, headers=headers)
        html.raise_for_status()  
        soup = BeautifulSoup(html.content, "html.parser")
        logging.info("Page fetched successfully!")
    
    except requests.exceptions.ConnectionError:
        result['message': "Connection error! Please check your internet connection."] 
        result['error_code': "1"]
        logging.error(result)
        return result
    
    except requests.exceptions.Timeout:
        result['message': 'The request timed out. Try again later.']
        result['error_code': '2']
        logging.error(result) 
        return result
    
    except Exception as e:
        result['message':'An unexpected error occurred: {e}']
        result['error_code':'3']
        logging.error(result) 
        return result
    
    # Extract rows from the table
    try:
        table_rows_list = soup.find_all('tr')
        if not table_rows_list or len(table_rows_list) < 1:
            logging.warning("No table rows found.")
            raise ValueError("No table rows found in the HTML content. The website structure might have changed.")
    except ValueError as ve:
        logging.error(f"Value error occurred: {ve}")
        result['message':'Value error occurred: {ve}']
        result['error_code':'4']
        return result

    # Clean rows' data
    cleaned_table_data_list = []    
    for row in table_rows_list[1:]:
        table_cells_list = row.find_all('td')
        cells_as_string = str(table_cells_list)
        html_tag_pattern = re.compile('<.*?>')
        cleaned_cells = re.sub(html_tag_pattern, '', cells_as_string)
        cleaned_table_data_list.append(cleaned_cells)

    # Convert cleaned data into a DataFrame
    cleaned_data_df = pd.DataFrame(cleaned_table_data_list)

    # Replace commas in numbers with | and split the data
    cleaned_data_df[0] = cleaned_data_df[0].str.replace(r'(\d),(\d)', r'\1|\2', regex=True)
    split_df = cleaned_data_df[0].str.split(',', expand=True)

    # Replace | back with commas in numbers
    for col in split_df.columns: 
        for index, value in split_df[col].items(): 
            if isinstance(value, str):  
                split_df.at[index, col] = value.replace('|', ',')  

    # Iterate through rows and columns to remove square brackets
    for row_index, row in split_df.iterrows():
        for col in split_df.columns:
            value = row[col]
            if isinstance(value, str):  
                split_df.at[row_index, col] = value.replace('[', '').replace(']', '')

    # Extract and clean table headers
    col_headers_list = soup.find_all('th')
    all_headers_list = []
    col_str = str(col_headers_list)
    cleantext = BeautifulSoup(col_str, "lxml").get_text()
    all_headers_list.append(cleantext)

    # Ensuring table headers exit
    if not col_headers_list:
        logging.warning("No headers found.")

    # Convert headers into a DataFrame
    header_df = pd.DataFrame(all_headers_list)
    header_df = header_df[0].str.split(',', expand=True)
    
    # Iterate through rows and columns to remove square brackets
    for row_index, row in header_df.iterrows(): 
        for col in header_df.columns:
            value = row[col]
            if isinstance(value, str):  
                header_df.at[row_index, col] = value.replace('[', '').replace(']', '')

    # Combine headers and data into one DataFrame
    concat_df = pd.concat([header_df, split_df])
    concat_df = concat_df.rename(columns=concat_df.iloc[0])

    # Drop duplicate header row
    population_df = concat_df.iloc[1:]

    # Replace Minus (`−`) with Hyphen (`-`)
    for row_index, row in population_df.iterrows():  
        for col in population_df.columns:  
            value = row[col]  
            if isinstance(value, str): 
                population_df.at[row_index, col] = value.replace('−', '-')  

    # Save the DataFrame to a CSV file
    population_df.to_csv(output_file_name, index=False, encoding='utf-8')

    logging.info("Scraping completed and data saved to 'world_population.csv'")

    # Returning final response
    result['success'] = 1
    result['message'] = "Scraping completed and data saved to 'world_population.csv'"
    logging.debug("Exiting scraper function")
    logging.info(result)
    return result


def main():


    """
    Calls the `scraper` function, updates the result based on its response, and handles unexpected exceptions.

    Returns:
        dict: A dictionary with the following keys:
            - success (int): 1 if the scraping is successful, 0 otherwise.
            - data (dict): An empty dictionary (placeholder for future enhancements).
            - message (str): A message summarizing the success or failure of the scraping.
            - error_code (str): A code representing the type of error (if any):
    """

    result = {'success': 0, 'data': {}, 'message': '', 'error_code': '0'}

    logging.info("Starting the scraper...")

    try:
        scraper_response = scraper()
        if scraper_response['success'] == 1:
            result['success'] = 1
            result['data'] = scraper_response['data']
            result['message'] = scraper_response['message']            
        else:
            result['message'] = scraper_response['message']
            result['error_code'] = scraper_response['error_code']
            # direct assign instead of assigning individually --> result = scraper_response
    
    except Exception as e:
        result['message'] = f"An error occured during scraping : {e}"
        result['error_code'] = '5'
        logging.error(result)
        return result
    
    logging.info("Scraping task finished!")
    logging.info(result)
    return result                                             

# Entry point for the script
if __name__ == "__main__":
    main()