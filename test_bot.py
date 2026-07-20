# test_sheets.py
import gspread

gc = gspread.service_account(filename="service_account.json")

# Paste a real Google Sheet URL you've shared with the service account
sheet_url = "https://docs.google.com/spreadsheets/d/1gJIPtPGoGhnqGKWL3H8JP765bUCBYAJmpjK_9mwsktM/edit?gid=0#gid=0"
sheet_key = sheet_url.split("/d/")[1].split("/")[0]

sh = gc.open_by_key(sheet_key)
ws = sh.worksheet("Sheet1")

ws.append_rows([["テスト", "てすと", "test"]])
print("Success — check your sheet!")