import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse


def download_files(session, base_url, save_path):
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    response = session.get(base_url)
    if response.status_code != 200:
        print(f"Failed to access {base_url}")
        return

    if "Web Login Service" in response.text:
        print("Your Auth CAS cookie is invalid.")
        exit()

    # check if it is a directory
    soup = BeautifulSoup(response.text, "html.parser")
    for link in soup.find_all("a"):
        href = link.get("href")
        if href == "../":
            continue

        full_url = urljoin(base_url, href)
        parsed_base = urlparse(base_url)
        parsed_full_url = urlparse(full_url)

        # Check Scope
        if parsed_base.netloc != parsed_full_url.netloc or not full_url.startswith(base_url):
            print(f"Skipping external or invalid link: {full_url}")
            continue

        local_path = os.path.join(save_path, href)


        if href.startswith("?"):
            continue

        if href.endswith("/"):  # if is directory, recursive
            download_files(session, full_url, local_path)
        else:  # if is file, download
            download_file(session, full_url, local_path)


def download_file(session, file_url, save_path):
    print(f"Downloading {file_url}...")
    response = session.get(file_url, stream=True)
    if response.status_code == 200:
        with open(save_path, "wb") as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
    else:
        print(f"Failed to download {file_url}")


# 主程序
if __name__ == "__main__":
    auth = input("Enter your AUTH_CAS: ")
    semester_year = input("Enter the semester year (e.g., 2024_2025 or leave empty for the latest): ").strip()
    course_name = input("Enter the course name (e.g., CS3105): ").strip()

    if semester_year:
        base_url = f"https://studres.cs.st-andrews.ac.uk/{semester_year}/{course_name}/"
    else:
        base_url = f"https://studres.cs.st-andrews.ac.uk/{course_name}/"

    save_directory = f"./{course_name}"

    headers = {
        "Cookie": f"MOD_AUTH_CAS_S={auth}",
    }

    session = requests.Session()
    session.headers.update(headers)

    download_files(session, base_url, save_directory)
