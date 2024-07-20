# DOU Python technologies statistics

## Overview
This project requires a combination of Web Scraping & Data Analysis skills. The aim is to help you understand the most demanded
technologies in the tech market right now. For example, to become a Python Developer, you need to know Django/Flask, Web, PostgreSQL.
However, even these technologies may not be as popular at the moment you search for jobs.
To be more prepared for interviews and to understand which technologies you should learn, this project creates statistics of the most 
demanded technologies based on DOU vacancies for Python Developers.

## Features
- Scrape job listings from https://jobs.dou.ua/
- Analyze and visualize the most mentioned technologies
- Breakdown job listings by location and experience level

## Setup
1. Clone the repository:
```
git clone https://github.com/oleksandra-shershen/dou-vacancies-analysis.git
cd dou-vacancies-analysis
```

2. Create and activate a virtual environment

On Windows:
```
python -m venv venv 
venv\Scripts\activate
```
On UNIX or macOS:
```
python3 -m venv venv 
source venv/bin/activate
```

3. Install the dependencies
```
pip install -r requirements.txt
```

4. Start scraping
```
python scraper/scraper.py
```
## Result of data analysis
![image](https://github.com/user-attachments/assets/f71c1266-a493-4b83-b4c8-093f139c3db5)

## Contributing
If you want to contribute to the project, please follow these steps:

- Fork the repository.
- Create a new branch for your feature or bug fix.
- Make the necessary changes and commit them.
- Submit a pull request.
