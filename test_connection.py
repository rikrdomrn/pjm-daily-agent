# test_connection.py
import anthropic
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Test Claude API
client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "Hello! Just testing the connection."}
    ]
)

print("✅ Claude API connected successfully!")
print(f"Response: {message.content[0].text}")