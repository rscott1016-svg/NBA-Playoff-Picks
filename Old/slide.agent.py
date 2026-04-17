import ollama
import pandas as pd

print("1. Agent is opening your financial records...")

# Mock data to start - later we will link this to your real files
transactions = [
    {"desc": "Icelandic Glacial Water", "amt": 45.00},
    {"desc": "10Cubed Midtown", "amt": 240.00},
    {"desc": "MTA MetroCard", "amt": 34.00},
    {"desc": "Max Streaming", "amt": 16.99}
]

categorized_data = []

print("2. AI is categorizing expenses locally...")

for item in transactions:
    prompt = f"Categorize this expense in one word (e.g. Food, Travel, Home, Bills): {item['desc']}"
    response = ollama.chat(model='llama3.2:1b', messages=[{'role': 'user', 'content': prompt}])
    category = response['message']['content'].strip().replace('.', '')
    
    categorized_data.append({
        "Description": item['desc'],
        "Amount": item['amt'],
        "Category": category
    })

# 3. Create the Excel Budget
print("3. Saving your Private Budget to Excel...")
df = pd.DataFrame(categorized_data)
df.to_excel("My_Private_Budget.xlsx", index=False)

print("--- SUCCESS! 'My_Private_Budget.xlsx' created locally ---")
