import mediacloud.api, datetime, os, re, unidecode 
import pandas as pd
import argparse, configparser

project_root = os.path.dirname(os.path.abspath(__file__))


def kw_file_reader(file_path): 
    '''
    reading keywords from keyword list in input folder
    '''
    keyWords = []
    with open(file_path, mode = 'r', encoding='utf-8') as f:
        for line in f:
            keyWords += [line.strip()]
    print(f'Keywords: {keyWords}\n')
    return keyWords

def save_csv (database=pd.DataFrame(), file_name=''):
    '''
    outputs query dataFrame (drop duplicates) to one csv and per publication url counts to another csv
    '''
    if len(database.index) == 0:
        print(f'Query {file_name} returned no articles')
    else:
        database.drop_duplicates(keep='first').to_csv(project_root+'/output/{0}.csv'.format(file_name), encoding='utf-8', index=False, header=True)
        print ('File: {0}.csv saved on output folder'.format(file_name))
        pubs = database["media_name"].value_counts()
        pubs.to_csv(f'./output/urls_per_publication_{file_name}.csv', header = True, encoding = 'utf-8')

def fn_cleaner(kw):
    '''
    cleans query to write a clean output file name 
    '''
    regex = re.compile(r'[/\s \W+ /]')
    unaccented_string = unidecode.unidecode(kw)
    # print(unaccented_string)
    clean_kw = regex.sub('',unaccented_string)
    # print(clean_kw)
    return clean_kw

def api_query(input_fp, collectionId, keyAPI, startDate, endDate):
    
    mc = mediacloud.api.MediaCloud(keyAPI)
    keyWords = kw_file_reader(file_path=input_fp)

    time_format = "%Y-%m-%d" 
    startDate = datetime.datetime.strptime(startDate, time_format) ##yyyy-mm-dd
    endDate = datetime.datetime.strptime(endDate, time_format) ##yyyy-mm-dd

    for kw in keyWords:

        geo_query = f'({kw}) AND tags_id_media:{collectionId}'
        print(geo_query)

        fetch_size = 500
        stories = []
        last_processed_stories_id = 0
        while len(stories) < 35000:
            fetched_stories = mc.storyList(solr_query = geo_query, 
                                        solr_filter=mc.dates_as_query_clause(startDate, endDate),
                                        last_processed_stories_id=last_processed_stories_id, rows= fetch_size)
            stories.extend(fetched_stories)
            if len( fetched_stories) < fetch_size:
                break
            last_processed_stories_id = stories[-1]['processed_stories_id']

        db_mediaOutput = pd.DataFrame()
        for article in stories:

            newObject = {
                'keyword'     : kw,
                'article_id'  : str(article['processed_stories_id']),
                'title'       : article['title'],
                'article_url' : article['url'],
                'media_id'    : str(article['media_id']),
                'media_name'  : article['media_name'],
                'publish_date': article['publish_date'],
                'stories_id'  : str(article['stories_id'])
            }

            db_mediaOutput = db_mediaOutput.append(newObject, ignore_index=True)

        file_name = fn_cleaner(kw=kw)
        save_csv (database = db_mediaOutput, file_name = f'{file_name}_{collectionId}')


if __name__ == "__main__":

    # SET UP Mediacloud API key
    configparser = configparser.ConfigParser()
    config_file = "./config.ini"

    configparser.read(config_file)
    keyAPI = configparser.get("mc_api", "mediacloud_key")

    parser = argparse.ArgumentParser(description='Querying the Mediacloud API from CLI.')
    parser.add_argument('--input_fp', required=True, type=str,
                        help='Input file path - should contain one query per line following the adequate Mediacloud syntax.')
    parser.add_argument('--collectionId', required=True, type=int,
                        help='Collection id of the Mediacloud geo collection')
    parser.add_argument('--startDate', required=True, type= str,
                        help='Date string for start of query interval - format YYYY-MM-DD')
    parser.add_argument('--endDate', required=True, type = str,
                        help='Date string for end of query interval - format YYYY-MM-DD')
                        
    args = parser.parse_args()
    api_query(input_fp = args.input_fp, collectionId=args.collectionId, keyAPI=keyAPI, startDate=args.startDate, endDate=args.endDate)