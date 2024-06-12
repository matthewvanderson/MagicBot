import base64
import json
import aiohttp
from urllib.parse import quote, unquote

#data = {'messages': [{'data': {'content': 'fuck', 'embeds': [{'title': "What's this about?", 'description': 'fuck fuck fuck', 'color': 5814783}], 'attachments': []}}]}

def encoded_data(data: dict):
    if data.get("embeds") == []:
        data["embeds"] = None
    data['attachments'] = []
    data = {"messages" : [{"data" : data}]}

    json_string = json.dumps(data, separators=(',', ':'), sort_keys=True)

    # Encode the JSON string to base64
    base64_encoded = base64.b64encode(json_string.encode('utf-8')).decode('utf-8')

    # Remove any '=' padding characters
    base64_encoded = base64_encoded.rstrip('=')

    # Replace '+' with '%2B' for URL encoding
    base64_encoded = base64_encoded.replace('+', '%2B')

    # Since the decoding side expects '%3D' to replace '=', add '=' signs back for URL encoding.
    # But this is not typically how you would handle base64 in URL parameters.
    # Instead, let's ensure that '=' is handled correctly in URL encoding scenarios.
    # This depends on whether your decoding logic expects '%3D' or '=' directly.
    # Comment out the next line if your decoder does not convert '%3D' back to '='.
    base64_encoded = base64_encoded.replace('=', '%3D')

    return base64_encoded


def reverse_encoding(base64_encoded: str):
    # Step 1: Replace `%2B` with `+`. The replacement of `=` with `%3D` might not be necessary here, as the decoding step will handle URL-encoded values.
    base64_encoded = base64_encoded.replace("%2B", "+")

    # Step 2: Add back the removed `=` padding. The length of base64 string should be a multiple of 4.
    padding_needed = len(base64_encoded) % 4
    if padding_needed:  # If padding is needed, add the necessary amount of '=' characters.
        base64_encoded += '=' * (4 - padding_needed)

    # Step 3: Decode the base64-encoded string.
    decoded_data = base64.b64decode(base64_encoded)

    # Step 4: URL-decode this string.
    json_string = unquote(decoded_data.decode('utf-8'))

    # Step 5: Parse the JSON string back into a Python dictionary.
    embed_dict = json.loads(json_string)

    data = dict(embed_dict).get("messages")[0].get("data")
    data.pop("attachments", None)
    if data.get("embeds") is None:
        data["embeds"] = []
    return data



async def shorten_link(url: str):
    api_url = "https://api.clashking.xyz/shortner"
    params = {'url': url}
    async with aiohttp.ClientSession() as session:
        async with session.get(api_url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("url")
            else:
                return None