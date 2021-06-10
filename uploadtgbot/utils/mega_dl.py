from base64 import b64decode
from codecs import latin_1_decode, latin_1_encode
from json import dumps, loads
from random import randint
from re import findall, search
from struct import pack, unpack

from Crypto.Cipher import AES
from httpx import AsyncClient, post


async def aes_cbc_decrypt(data, key):
    aes_cipher = AES.new(key, AES.MODE_CBC, latin_1_encode("\0" * 16)[0])
    return aes_cipher.decrypt(data)


async def decrypt_attr(attr, key):
    attr = await aes_cbc_decrypt(attr, (await a32_to_str(key)))
    attr = latin_1_decode(attr)[0]
    attr = attr.rstrip("\0")
    return loads(attr[4:]) if attr[:6] == 'MEGA{"' else False


async def a32_to_str(a):
    return pack(">%dI" % len(a), *a)


async def str_to_a32(b):
    if isinstance(b, str):
        b = latin_1_encode(b)[0]
    if len(b) % 4:
        b += b"\0" * (4 - len(b) % 4)
    return unpack(">%dI" % (len(b) / 4), b)


async def base64_url_decode(data):
    data += "=="[(2 - len(data) * 3) % 4 :]
    for search, replace in (("-", "+"), ("_", "/"), (",", "")):
        data = data.replace(search, replace)
    return b64decode(data)


async def base64_to_a32(s):
    return await str_to_a32(await base64_url_decode(s))


async def parse_url(url):
    if "/file/" in url:
        url = url.replace(" ", "")
        file_id = findall(r"\W\w\w\w\w\w\w\w\w\W", url)[0][1:-1]
        id_index = search(file_id, url).end()
        key = url[id_index + 1 :]
        return f"{file_id}!{key}"
    elif "!" in url:
        match = findall(r"/#!(.*)", url)
        path = match[0]
        return path
    else:
        return None


async def download_file(url):
    path = (await parse_url(url)).split("!")
    if path == None:
        return None, None, None
    file_handle = path[0]
    file_key = path[1]
    file_key = await base64_to_a32(file_key)
    file_data = await api_request({"a": "g", "g": 1, "p": file_handle})
    k = (
        file_key[0] ^ file_key[4],
        file_key[1] ^ file_key[5],
        file_key[2] ^ file_key[6],
        file_key[3] ^ file_key[7],
    )
    if "g" not in file_data:
        return None, None, None
    file_url = file_data["g"]
    file_size = file_data["s"]
    attribs = await base64_url_decode(file_data["at"])
    attribs = await decrypt_attr(attribs, k)
    file_name = attribs["n"]
    return file_name, file_size, file_url


async def api_request(data):
    sequence_num = randint(0, 0xFFFFFFFF)
    if not isinstance(data, list):
        data = [data]
    url = f"https://g.api.mega.co.nz/cs"
    params = {"id": sequence_num}
    async with AsyncClient():
        response = post(url, data=dumps(data), params=params)
    json_resp = response.json()
    return json_resp[0]
