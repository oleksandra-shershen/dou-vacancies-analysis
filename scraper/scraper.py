import csv
import os
import asyncio
import re
from aiohttp import ClientSession
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

from config import TECHNOLOGIES, VACANCIES_URL


def click_all_load_more_buttons(driver: webdriver.Chrome) -> None:
    page_number = 1
    while True:
        try:
            load_more_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".more-btn a"))
            )
            if "display: none" in load_more_button.get_attribute("style"):
                break

            load_more_button.click()

            page_number += 1
        except Exception:
            break


async def fetch_detailed_description(session: ClientSession, job_url: str) -> dict:
    async with session.get(job_url) as response:
        job_page = await response.text()
        soup = BeautifulSoup(job_page, "html.parser")
        job_description_div = soup.find("div", class_="b-typo vacancy-section")
        if job_description_div:
            job_description = job_description_div.text.strip()
            job_description = job_description.replace("\xa0", " ")
        else:
            job_description = "No description available"

        city_span = soup.find("span", class_="place bi bi-geo-alt-fill")
        if city_span:
            city = city_span.text.strip()
        else:
            city = "Unknown"

        requirements = [tech for tech in TECHNOLOGIES if tech.lower() in job_description.lower()]

        # Extract experience using regex
        experience_match = re.search(r'(\d+\+ years)', job_description)
        experience = experience_match.group(0) if experience_match else "Not specified"

        return {
            "description": job_description,
            "city": city,
            "requirements": ", ".join(requirements),
            "experience": experience
        }


async def fetch_all_descriptions(job_listings: list) -> list:
    async with ClientSession() as session:
        tasks = []
        for job in job_listings:
            task = asyncio.ensure_future(
                fetch_detailed_description(session, job["url"])
            )
            tasks.append(task)
        descriptions = await asyncio.gather(*tasks)
        for i, job in enumerate(job_listings):
            job["description"] = descriptions[i]["description"]
            job["city"] = descriptions[i]["city"]
            job["requirements"] = descriptions[i]["requirements"]
            job["experience"] = descriptions[i]["experience"]
        return job_listings


def parse_page(driver: webdriver.Chrome) -> list:
    soup = BeautifulSoup(driver.page_source, "html.parser")
    vacancy_cards = soup.find_all("li", class_="l-vacancy")
    job_listings = []
    for vacancy in vacancy_cards:
        title_tag = vacancy.find("a", class_="vt")
        company_tag = vacancy.find("a", class_="company")
        if title_tag and company_tag:
            title = title_tag.text.strip()
            url = title_tag["href"]
            company = company_tag.text.strip()
            job_listings.append(
                {
                    "title": title,
                    "url": url,
                    "company": company,
                    "description": "",
                    "city": "",
                    "requirements": "",
                    "experience": ""
                }
            )
    return job_listings


def remove_duplicates_from_requirements(vacancies: list) -> list:
    for vacancy in vacancies:
        requirements = vacancy["requirements"].split(", ")
        unique_requirements = sorted(set(requirements), key=requirements.index)
        vacancy["requirements"] = ", ".join(unique_requirements)
    return vacancies


def write_to_csv(vacancies: list, filename: str) -> None:
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["title", "url", "company", "description", "city", "requirements", "experience"])
        for vacancy in vacancies:
            writer.writerow(
                [
                    vacancy["title"],
                    vacancy["url"],
                    vacancy["company"],
                    vacancy["description"],
                    vacancy["city"],
                    vacancy["requirements"],
                    vacancy["experience"]
                ]
            )


async def get_all_vacancies() -> None:
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=chrome_options
    )
    driver.get(VACANCIES_URL)

    click_all_load_more_buttons(driver)

    job_listings = parse_page(driver)
    detailed_job_listings = await fetch_all_descriptions(job_listings)
    unique_detailed_job_listings = remove_duplicates_from_requirements(detailed_job_listings)

    write_to_csv(unique_detailed_job_listings, "data/vacancies.csv")
    driver.quit()


if __name__ == "__main__":
    asyncio.run(get_all_vacancies())
