import json
import os
import pandas as pd
import shutil

QUOTE_ALL = int(1)  # to prevent loading csv library https://docs.python.org/3/library/csv.html just using the value of csv.QUOTE_ALL

with open("doc_parameters.json", 'r') as parametersfile:
    parameters = json.load(parametersfile)
    
# return ./input when not found in parameters.json
input_path = parameters.get("filepaths", {}).get("inputfolder", "./input/")

# return input.csv when not found in parameters.jsoncd 
input_file = parameters.get("filepaths", {}).get("inputfile", "input.csv")

# return ./output when not found in parameters.json
output_path = parameters.get("filepaths", {}).get("outputfolder", "./output/")

# if no value is given assumes Excel 97-2003 workbook size
max_excel_lines = int(parameters.get("output", {}).get("max_excel_lines", 65535))

if not os.path.exists(output_path):
    os.makedirs(output_path)

df_zaak_informatie = pd.read_csv(input_path+input_file, sep=";", quotechar='"', dtype=str)
print("Aantal ingelezen zaakregels:", str(len(df_zaak_informatie)))

df_check_info = df_zaak_informatie[["ZAAKTYPE_NAAM", "SQUITXO_HOOFDZAAKNUMMER","EXTERN_ZAAKNUMMER","FULL_DOCUMENT_PATH","SQUITXO_ZAAKNUMMER_AANGEPAST_B","SQUITXO_ZAAKNUMMER_AANGEPAST_B_PUNT","SQUITXO_ZAAKNUMMER_AANGEPAST_S"]].copy()
df_check_info.rename(columns=
    {"SQUITXO_ZAAKNUMMER_AANGEPAST_B": "VARIANT1_B",
     "SQUITXO_ZAAKNUMMER_AANGEPAST_B_PUNT": "VARIANT2_Bpunt",
     "SQUITXO_ZAAKNUMMER_AANGEPAST_S": "VARIANT3_S"},
     inplace=True)

df_check_info.reset_index(drop=True, inplace=True)
df_check_info["FILE_FOUND"]="NEE"
df_check_info["OUTPUT_PATH"] = ""
df_check_info["OUTPUT_FILE"] = ""
df_check_info["COULD_COPY_FILE"] = "NEE"
print("Aantal te checken zaakregels:", str(len(df_check_info)))

df_check_info.drop(df_check_info.loc[df_check_info["FULL_DOCUMENT_PATH"] == "NOT AVAILABLE"].index, inplace=True)
print("Waarvan zaakregels met lokaal document:", str(len(df_check_info)))

aantal_gelukt = 0
for index, row in df_check_info.iterrows():
    
    if os.path.isfile(row["FULL_DOCUMENT_PATH"]):
        df_check_info.at[index, "FILE_FOUND"] = "JA"
        # print(os.path.split(row["FULL_DOCUMENT_PATH"]))
        df_check_info.at[index, "OUPTUT_PATH"] = output_path
        filename_to_copy = os.path.split(row["FULL_DOCUMENT_PATH"])[1]  # get the tail part
        df_check_info.at[index, "OUPTUT_file"] = filename_to_copy
        source_path = row["FULL_DOCUMENT_PATH"]
        zaaknummer = row["SQUITXO_HOOFDZAAKNUMMER"]
        destination_path = output_path+zaaknummer+"/"+filename_to_copy
        
        try:
            shutil.copyfile(source_path, destination_path)
            df_check_info.at[index, "COULD_COPY_FILE"] = "JA"
            aantal_gelukt += 1
                    
        except Exception as error:
            print(error)

print("Aantal op te slaan zaakregels:", str(len(df_check_info)))  
print("Waarvan gelukte documenten   :", str(aantal_gelukt)) 

df_check_info.to_csv(output_path+"df_check_info.csv", index=False, sep=";", quotechar='"', quoting=QUOTE_ALL)       
df_check_info.to_excel(output_path+"df_check_info.xlsx", index=False)
    