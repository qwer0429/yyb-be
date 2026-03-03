import re
import requests
import json
import pandas as pd

ids = []
username_lst = []

def adduserfromexcel():
    userinfo_lst = []
    excel_file = pd.ExcelFile("E:\原研宝.xlsx")
    for sheet_name in excel_file.sheet_names:
        df = excel_file.parse(sheet_name)
        for i in range(1, len(df)):
            userinfo = df.iloc[i].to_dict()
            if not userinfo['drug_name'] or type(userinfo['drug_name'])!=str:
                break
            userinfo_lst.append(userinfo)
            print(userinfo)
    print(type(userinfo_lst[-1]['drug_name']))
    print(len(userinfo_lst))
    return userinfo_lst
    


userinfo_lst = adduserfromexcel()