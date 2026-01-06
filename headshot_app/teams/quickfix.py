import pandas as pd 
df = pd.read_csv("wcc_roster.csv")

names = [
    "Lucia Navarro",
    "Ilinca Belegante",
    "Coco Urlacher",
    "Mackenzie Shivers",
    "Catarina Ferreira",
    "Vera Gunaydin",
    "Alia Matavao",
    "Maddy Warberg",
    "Sara Schmerbach",
    "Reilly Clark",
    "Colleena Bryant",
    "Noelia Mourino",
    "Tahara Magassa",
    "Goundo Diakite Bayo",
    "Camille Dake",
    "Ryanne Bahnsen-Price",
    "Lauren McCall",
    "Lova Lagerlid",
    "Kenlee Durrill",
    "Quinn VanSickle",
    "Mari Somvichian",
    "Tyla Fautua",
    "Allison Clarke",
    "Elisa Mehyar",
    "Zoe Shanahan",
]
df = df[~((df['Full Name'].isin(names)) | (df['Team'] == 'lmu'))]
print("\n")
df.to_csv("wcc_roster2.csv",index=False)