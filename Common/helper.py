import requests

API_URL = "https://api-inference.huggingface.co/models/Hate-speech-CNERG/bert-base-uncased-hatexplain"
headers = {"Authorization": "Bearer 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"}

def query(payload):
	response = requests.post(API_URL, headers=headers, json=payload)
	return response.json()
	
if __name__ == "__main__":
    output = query({
	    "inputs": "I like you. I love you",
    })
    print(output)