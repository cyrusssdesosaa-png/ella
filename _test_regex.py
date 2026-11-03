import re
text = "I'm Cyrus, your local AI assistant."
m = re.search(r"\bI'?m Cyrus\b", text, re.IGNORECASE)
print("match:", m)
fixed = re.sub(r"\bI'?m Cyrus\b", "I'm Ella", text, flags=re.IGNORECASE)
print("fixed:", fixed)

# Unicode apostrophe variant
text2 = "I\u2019m Cyrus, your local AI assistant."
m2 = re.search(r"\bI'?m Cyrus\b", text2, re.IGNORECASE)
print("unicode match:", m2)
# Fix: also match unicode apostrophe
m3 = re.search(r"\bI[\u2019']?m Cyrus\b", text2, re.IGNORECASE)
print("unicode2 match:", m3)
