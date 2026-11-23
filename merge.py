import requests
import re

# 原仓库基础地址与主入口，不改动
BASE_URL = "https://raw.githubusercontent.com/Kimentanm/aptv/master/m3u/"
MAIN_URL = BASE_URL + "iptv.m3u"

# 输出文件名
OUTPUT_FILE = "universal.m3u"

def fetch(url):
    """下载文件内容"""
    try:
        r = requests.get(url, timeout=20)
        r.encoding = "utf-8"
        return r.text
    except Exception as e:
        print(f"下载失败 {url}: {e}")
        return ""

def clean_content(text):
    """清理所有APTV私有标签，保留标准M3U内容与原排序"""
    lines = text.splitlines()
    result = []
    for line in lines:
        # 跳过APTV专属整行标签
        if line.startswith(("#EXT-X-APP", "#EXT-X-APTV-", "#EXT-X-SUB-URL")):
            continue
        # 去掉子文件重复的 #EXTM3U 头，最后统一加
        if line.strip() == "#EXTM3U":
            continue
        # 清理行内私有参数 http-user-agent
        line = re.sub(r'\s+http-user-agent="[^"]*"', '', line)
        result.append(line)
    return "\n".join(result)

def main():
    print("开始拉取主源...")
    main_text = fetch(MAIN_URL)
    if not main_text:
        print("主源下载失败，终止")
        return

    # 按原文件顺序提取所有嵌套子文件
    sub_list = re.findall(r"#EXT-X-SUB-URL\s+(.+)", main_text)
    print(f"解析到 {len(sub_list)} 个子文件，按原顺序合并")

    # 拼接完整下载地址
    full_urls = []
    for item in sub_list:
        filename = item.strip().split("/")[-1]
        full_urls.append(BASE_URL + filename)

    # 按原顺序合并所有内容
    final = ["#EXTM3U"]
    for idx, url in enumerate(full_urls):
        fname = url.split("/")[-1]
        print(f"正在合并 [{idx+1}/{len(full_urls)}]: {fname}")
        content = fetch(url)
        if not content:
            continue
        final.append(clean_content(content))

    # 保存输出
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(final).strip())
    print(f"合并完成，已生成 {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
