import pandas as pd
df = pd.read_csv("lmugamelog0105.csv")
# cols = Name,Jersey #,Team,Opponent,didWin,Date,MIN,OREB,DREB,REB,AST,STL,BLK,TO,PF,FGM,FGA,3PM,3PA,FTM,FTA,efg%,PTS,FantasyPts,isWCC,weeknum
# print opponent rows where 'Team' != 'Loyola Marymount Lions'
df2 = df[df['Team'] != 'Loyola Marymount Lions']
df2 = df2.sort_values(by='3PA',ascending=False)
df2 = df2[['Name','Team','3PM','3PA','PTS']]
df2.to_csv('lmuopponents.csv',index = False)