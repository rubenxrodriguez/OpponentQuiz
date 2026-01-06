import pandas as pd 
df = pd.read_csv('fantasy_stats_2025-12-27.csv')
df = df.sort_values(by='FantasyPts_sum', ascending=False).head(120)
#print(df['#'].unique())
#print(df['#'].value_counts())
#print(df.tail())
df2 = pd.read_csv("wcc_roster.csv")
#print(df2['Hometown'].value_counts())
df2['Hometown'].value_counts().to_csv("hometown_counts.csv", index=True)