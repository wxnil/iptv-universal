import requests
import re

BASE_URL = "https://raw.githubusercontent.com/Kimentanm/aptv/master/m3u/"
MAIN_URL = BASE_URL + "iptv.m3u"
OUTPUT_FILE = "universal.m3u"

def fetch(url):
    try:
        r = requests.get(url, timeout=20)
        r.encoding = "utf-8"
        return r.text
    except Exception as e:
        print(f"下载失败 {url}: {e}")
        return ""

def clean_content(text):
    lines = text.splitlines()
    result = []
    for line in lines:
        # 跳过APTV专属整行标签
        if line.startswith(("#EXT-X-APP", "#EXT-X-APTV-", "#EXT-X-SUB-URL")):
            continue

        # 处理EXTINF行，提取 http-user-agent，转成EXTVLCOPT
        if "#EXTINF" in line:
            match = re.search(r'\s+http-user-agent="([^"]+)"', line)
            if match:
                ua_val = match.group(1)
                # 删掉行内的aptv私有参数
                line = re.sub(r'\s+http-user-agent="[^"]*"', '', line)
                result.append(line)
                # 新增一行标准VLC UA标签
                result.append(f'#EXTVLCOPT:http-user-agent={ua_val}')
            else:
                result.append(line)
        elif line.strip() == "#EXTM3U":
            continue
        else:
            result.append(line)
    return "\n".join(result)

def main():
    print("开始拉取主源...")
    main_text = fetch(MAIN_URL)
    if not main_text:
        print("主源下载失败，终止")
        return

    sub_list = re.findall(r"#EXT-X-SUB-URL\s+(.+)", main_text)
    print(f"解析到 {len(sub_list)} 个子文件，按原顺序合并")

    full_urls = []
    for item in sub_list:
        filename = item.strip().split("/")[-1]
        full_urls.append(BASE_URL + filename)

    final = ["#EXTM3U"]
    for idx, url in enumerate(full_urls):
        fname = url.split("/")[-1]
        print(f"正在合并 [{idx+1}/{len(full_urls)}]: {fname}")
        content = fetch(url)
        if not content:
            continue
        final.append(clean_content(content))

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(final).strip())
    print(f"合并完成，已生成 {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
