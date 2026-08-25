from agent.sql_agent import ask

print("Testing SQL Agent...")
print("-" * 50)

response1 = ask("How many customers are there?")
print("Q: How many customers are there?")
print(f"A: {response1}")
print("-" * 50)

response2 = ask("Which country has the most customers?")
print("Q: Which country has the most customers?")
print(f"A: {response2}")
print("-" * 50)