import asyncio
import requests
from flask import Flask, request, jsonify
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)

async def fetch_numbers(url):
    try:
        response = await asyncio.to_thread(requests.get, url, timeout=0.5)
        if response.status_code == 200:
            data = response.json()
            return data.get("numbers", [])
    except (requests.exceptions.Timeout, requests.exceptions.RequestException):
        pass
    return []
async def fetch_all_numbers(urls):
    tasks = [fetch_numbers(url) for url in urls]
    return await asyncio.gather(*tasks)

@app.route('/numbers', methods=['GET'])
def get_numbers():
    urls = request.args.getlist('url')
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        fetched_numbers = loop.run_until_complete(fetch_all_numbers(urls))
    finally:
        loop.close()

    merged_numbers = sorted(set(number for numbers in fetched_numbers for number in numbers))
    return jsonify({"numbers": merged_numbers})

if __name__ == '__main__':
    app.run(host='localhost', port=8008)