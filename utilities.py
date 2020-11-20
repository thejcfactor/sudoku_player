import requests
from requests.adapters import HTTPAdapter
from requests.sessions import default_headers
from urllib3.util import Retry
from bs4 import BeautifulSoup
import time

def back_off(tries, backoff_factor=0.3):
    seconds = backoff_factor * ( 2** (tries-1) )
    time.sleep(seconds)

def is_null_or_empty(str):
    """
    Returns True if str is None or str is empty or blank.  Returns False otherwise.
    """
    if str and str.strip():
        return False
    
    return True


def retry_wrapper(retries=3, back_off=0.5, status_force_list=(500,502,504)):
    session = requests.Session()
    retry = Retry(total=retries, 
        read=retries, 
        connect=retries,
        backoff_factor=back_off, 
        status_forcelist=status_force_list)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    return session

def get_page(url, timeout=60, retries=3, backoff_factor=0.5):
        
        if is_null_or_empty(url):
            return None

        tries = 0
        response = None
        while True:
            try:
                response = retry_wrapper().get(url, timeout=timeout)

                if response and response.status_code == 200:
                    #soup = BeautifulSoup(response.text, 'html.parser')
                    #print(soup.prettify())
                    break
                else:
                    raise Exception

            except Exception as ex:
                print(ex)
                tries = tries + 1
                if tries <= retries:
                    back_off(tries,backoff_factor)
                    continue
                else:
                    response = None
                    break

        return response

def get_new_board(url):
    print('Attempting to get new puzzle from:  {0}'.format(url))
    try:
        response = get_page(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        div = soup.find('div', {'id':'sudoku'})
        if not div:
            return None

        rows = div.find('table').find_all('tr', id=lambda x: x and x.startswith('line'))
        board = []
        for row in rows:
            tds = row.find_all('td')
            board_row = []
            for col in tds:
                default = col.find('span', {'class': 'sedy'})
                if default:
                    #print(default)
                    board_row.append(int(default.text))
                else:
                    board_row.append(0)
            board.append(board_row)

        return board
    except Exception as ex:
        print(ex)
        return None

