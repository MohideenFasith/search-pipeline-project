import requests

def evaluate(config_file, object_ids, email):
    url = "https://mercor-dev--search-eng-interview.modal.run/evaluate"
    headers = {
        "Authorization": email,
        "Content-Type": "application/json"
    }
    body = {
        "config_path": config_file,
        "object_ids": object_ids[:10]
    }
    res = requests.post(url, json=body, headers=headers)
    return res.json()

if __name__ == '__main__':
    sample_ids = ["67970d138a14699f1614c6b6", "679508a7a1a09a48feaadf0c"]
    print(evaluate("tax_lawyer.yml", sample_ids, "mohideenfasiths@gmail.com"))
