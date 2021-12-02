import pandas as pd
import glob, os

path = r'./output/'
all_files = glob.glob(os.path.join(path, "*.csv"))  # advisable to use os.path.join as this makes concatenation OS independent

dfs = []
for f in all_files:
  #excluding value count files produced in the MediacloudAPI call for each keyword
  #appending each dataFrame to a list for merging
  if f[len(path):len(path)+len('urls_per_publication')] != 'urls_per_publication':
    dfs += [pd.read_csv(f)]

frame = pd.concat(dfs, ignore_index=True) # doesn't create a list, nor does it append to one
#print(len(frame["stories_id"].unique())) # to confirm drop_duplicates is working

final_frame = frame.drop_duplicates(subset=["stories_id"],keep='last') #merged dataframe without duplicate rows
print(f'Number of articles: {final_frame.shape[0]}')

#summary statistic on number of articles per keyword (from dataFrame without duplicates)
keywords = final_frame["keyword"].value_counts()
keywords.to_csv('./merged/articles_per_keyword.csv', encoding='utf-8')

#summary statistic on number of articles per news publication (from dataFrame without duplicates)
pub = final_frame["media_name"].value_counts()
pub.to_csv('./merged/urls_per_publication.csv', encoding='utf-8' )

#writing the final dataFrame (merged from all keyword files and without duplicate) to a csv file
final_frame.to_csv('./merged/merged_output.csv', encoding = 'utf-8')