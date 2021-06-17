from re import findall, sub
from urllib.parse import unquote

from bs4 import BeautifulSoup
from httpx import get

from uploadtgbot.utils.display_progress import human_bytes
from uploadtgbot.utils.mega_dl import download_file


class DirectDl:
    def __init__(self, url: str):
        self.url = url

    async def check_url(self):
        if "sourceforge.net" in self.url:
            return self.sourceforge()
        elif "drive.google.com" in self.url:
            return self.gdrive()
        elif "yadi.sk" in self.url:
            return self.yandex_disk()
        elif "mediafire.com" in self.url:
            return self.mediafire()
        elif "osdn.net" in self.url:
            return self.osdn()
        elif "github.com" in self.url:
            return self.github()
        elif "mega.nz" or "mega.co.nz" in self.url:
            tmp = await download_file(self.url)
            name, size, link = tmp[0], tmp[1], tmp[2]
            return f"<b>Filename:</b> {name}\n<b>Size: {human_bytes(size)}</b>\n<b>Link:</b>\n{link}"
        return ""

    def gdrive(self):
        """GDrive direct links generator"""
        drive = "https://drive.google.com"
        try:
            link = findall(r"\bhttps?://drive\.google\.com\S+", self.url)[0]
        except IndexError:
            reply = "`No Google drive links found`\n"
            return reply
        file_id, reply = "", ""
        if link.find("view") != -1:
            file_id = link.split("/")[-2]
        elif link.find("open?id=") != -1:
            file_id = link.split("open?id=")[1].strip()
        elif link.find("uc?id=") != -1:
            file_id = link.split("uc?id=")[1].strip()
        url = f"{drive}/uc?export=download&id={file_id}"
        download = get(url, allow_redirects=False)
        cookies = download.cookies
        try:
            # In case of small file size, Google downloads directly
            dl_url = download.headers["location"]
            if "accounts.google.com" in dl_url:  # non-public file
                reply += "`Link is not public!`\n"
                return reply
            name = "Direct Download Link"
        except KeyError:
            # In case of download warning page
            page = BeautifulSoup(download.content, "lxml")
            export = drive + page.find("a", {"id": "uc-download-link"}).get("href")
            name = page.find("span", {"class": "uc-name-size"}).text
            response = get(
                export,
                allow_redirects=False,
                cookies=cookies,
            )
            dl_url = response.headers["location"]
            if "accounts.google.com" in dl_url:
                reply += "Link is not public!"
                return reply
        reply += f"[{name}]({dl_url})\n"
        return reply

    def yandex_disk(self):
        """Yandex.Disk direct links generator"""
        reply = ""
        try:
            link = findall(r"\bhttps?://.*yadi\.sk\S+", self.url)[0]
        except IndexError:
            reply = "`No Yandex.Disk links found`\n"
            return reply
        url = "https://cloud-api.yandex.net/v1/disk/"
        api = "{}public/resources/download?public_key={}".format(
            url,
            link,
        )
        try:
            dl_url = get(api).json()["href"]
            name = dl_url.split("filename=")[1].split("&disposition")[0]
            reply += f"[{name}]({dl_url})\n"
        except KeyError:
            reply += "`Error: File not found / Download limit reached`\n"
            return reply
        return reply

    def mediafire(self):
        """MediaFire direct links generator"""
        try:
            link = findall(r"\bhttps?://.*mediafire\.com\S+", self.url)[0]
        except IndexError:
            reply = "`No MediaFire links found`\n"
            return reply
        reply = ""
        page = BeautifulSoup(get(link).content, "lxml")
        info = page.find("a", {"aria-label": "Download file"})
        dl_url = info.get("href")
        size = findall(r"\(.*\)", info.text)[0]
        name = page.find("div", {"class": "filename"}).text
        reply += f"[{name} {size}]({dl_url})\n"
        return reply

    def sourceforge(self):
        """SourceForge direct links generator"""
        try:
            link = findall(r"\bhttps?://.*sourceforge\.net\S+", self.url)[0]
        except IndexError:
            reply = "`No SourceForge links found`\n"
            return reply
        file_path = findall(r"files(.*)/download", link)[0]
        reply = f"Mirrors for __{file_path.split('/')[-1]}__\n"
        project = findall(r"projects?/(.*?)/files", link)[0]
        mirrors = (
            f"https://sourceforge.net/settings/mirror_choices?"
            f"projectname={project}&filename={file_path}"
        )
        page = BeautifulSoup(get(mirrors).content, "html.parser")
        info = page.find("ul", {"id": "mirrorList"}).findAll("li")
        for mirror in info[1:]:
            name = findall(r"\((.*)\)", mirror.text.strip())[0]
            dl_url = "https://{}.dl.sourceforge.net/project/{}/{}".format(
                mirror["id"],
                project,
                file_path,
            )
            reply += f"[{name}]({dl_url}) "
        return reply

    def osdn(self):
        """OSDN direct links generator"""
        osdn_link = "https://osdn.net"
        try:
            link = findall(r"\bhttps?://.*osdn\.net\S+", self.url)[0]
        except IndexError:
            reply = "`No OSDN links found`\n"
            return reply
        page = BeautifulSoup(
            get(
                link,
                allow_redirects=True,
            ).content,
            "lxml",
        )
        info = page.find("a", {"class": "mirror_link"})
        link = unquote(osdn_link + info["href"])
        reply = f"Mirrors for __{link.split('/')[-1]}__\n"
        mirrors = page.find("form", {"id": "mirror-select-form"}).findAll("tr")
        for data in mirrors[1:]:
            mirror = data.find("input")["value"]
            name = findall(r"\((.*)\)", data.findAll("td")[-1].text.strip())[0]
            dl_url = sub(r"m=(.*)&f", f"m={mirror}&f", link)
            reply += f"[{name}]({dl_url}) "
        return reply

    def github(self):
        """GitHub direct links generator"""
        try:
            link = findall(r"\bhttps?://.*github\.com.*releases\S+", self.url)[0]
        except IndexError:
            reply = "`No GitHub Releases links found`\n"
            return reply
        reply = ""
        dl_url = ""
        download = get(self.url, allow_redirects=False)
        try:
            dl_url = download.headers["location"]
        except KeyError:
            reply += "`Error: Can't extract the link`\n"
        name = link.split("/")[-1]
        reply += f"[{name}]({dl_url}) "
        return reply
