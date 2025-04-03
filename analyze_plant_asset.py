import json

# Load the JSON file
with open('plant_asset_output.json', 'r') as f:
    data = json.load(f)

# Print basic info
print('Total number of tables:', len(data['tables']))
print('Second table rows:', len(data['tables'][1]))

# Print categories in the second table
print('Categories in the second table:')
for row in data['tables'][1]:
    if len(row) > 0:
        # Check if this is a category header row (not a sub-question)
        if row[0] not in ['', 'a.', 'b.', 'c.', 'd.', 'e.', 'f.', 'g.', 'h.'] and not row[0].startswith('Can anyone'):
            if row[0] == "Yes" or row[0] == "No" or row[0] == "NA" or row[0] == "Comments":
                continue
            print(' -', row[0])