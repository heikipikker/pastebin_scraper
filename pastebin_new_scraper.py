import requests
import logging
import re
import time
import datetime

# Init logger
logger = logging.getLogger()
logging.basicConfig(level=logging.INFO, format='%(levelname)-8s %(message)s')
starttime=time.time()


def pastebin_init_processed_list():
    global saved
    saved = []
    with open('.processed_list.txt', 'r') as f:
        saved = [line.replace("\n", "") for line in f]

def pastebin_commit_processed_list():
    global saved
    with open('.processed_list.txt', 'w') as f:
        for key in saved:
            f.write("%s\n" % key)

def pastebin_check_if_processed(key):
    try:
        global saved
        if key in saved:
            logger.info("Key already saved : {}".format(key))
            return True
        else:
            logger.info("Key is not saved : {}".format(key))
            return False
    except Exception as e:
        logger.error("Error checking recent: {}".format(e))
        return False


# In[6]:


def pastebin_record_processed(key):
    try:
        global saved
        saved.append(key)
        logger.info("Saved key : {}".format(key))
    except Exception as e:
        logger.error("Error checking recent: {}".format(e))
        return False


# In[7]:


def pastebin_wait(seconds = 60):
    logger.info("Sleeping {} seconds.".format(seconds))
    time.sleep(seconds - ((time.time() - starttime) % seconds))


# In[8]:


def pastebin_get_recent(limit = 50):
    try:
        r = requests.get("https://scrape.pastebin.com/api_scraping.php?limit={}".format(limit))
        bins_dict = r.json()
        logger.info("Fetched {} items.".format(len(bins_dict)))
        return bins_dict
    except Exception as e:
        logger.error("Error fetching recent pastes: {}".format(e))
        return False


# In[9]:


def pastebin_get_raw(key=False):
    if not key:
        logger.error("No Key Set.")
        return False
    try:
        r = requests.get("https://scrape.pastebin.com/api_scrape_item.php?i={}".format(key))
        bins_dict = r.text
        logger.info("Fetched raw item for key: {}".format(key))
        return bins_dict
    except Exception as e:
        logger.error("Error fetching raw paste: {}".format(e))
        return False


# In[10]:


def pastebin_process_text(text):
    data = text.lower()
    if 'extinf' in data or '.m3u' in data:
        logger.info("Contains word EXTINF/.m3u")
        return False
    if len(re.findall(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", text)) >= 1:
        logger.info("Contains re IP ")
        return True
    if len(re.findall(r'[\w\.-]+@[\w\.-]+', text)) >= 1:
        logger.info("Contains re email ")
        return True
    if 'exploit' in data:
        logger.info("Contains word exploit")
        return True
    if 'pass' in data:
        logger.info("Contains word pass")
        return True
    if 'key' in data:
        logger.info("Contains word key")
        return True
    if 'database' in data:
        logger.info("Contains word database")
        return True
    if 'base64' in data:
        logger.info("Contains word base64")
        return True
    if 'fromcharcode' in data:
        logger.info("Contains word fromCharCode")
        return True
    return True


# In[11]:


def pastebin_write_to_file(key, text):
    config_dir = './pastebins/'
    try:
        with open("{}{}.txt".format(config_dir, key), "w") as f:
            f.write(text)
    except Exception as e:
        logger.error("Error writing to disk: {}".format(e))
        return False


# In[14]:


def main():
    pastebin_init_processed_list()
    latest_pastebins = pastebin_get_recent(250)
    if latest_pastebins:
        for pastebin in latest_pastebins:
            key = pastebin['key']
            date = datetime.datetime.fromtimestamp(int(pastebin['date'])).strftime("%Y-%m-%d %H:%M")
            size = pastebin['size']
            logger.info("Key: {}\t\tDate: {}\t\tSize: {}".format(key, date, size))
            if not pastebin_check_if_processed(key):
                raw_paste = pastebin_get_raw(key=key)
                valuable = pastebin_process_text(raw_paste)
                if valuable:
                    pastebin_write_to_file(key, raw_paste)
                pastebin_record_processed(key)
    pastebin_commit_processed_list()
    pastebin_wait(3*60.0)


# In[ ]:


if __name__ == "__main__":
    main()

