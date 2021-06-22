from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()




setup(
	name="python-cricket-scraper",
	version="0.1.0",
	description="python-cricket-scraper is built to get cricket data from Cricsheet and ESPNCricInfo",
	long_description=long_description,
	license="MIT",
	install_requires=["numpy", "pandas", "requests", "pyyaml"],
	author="Kaushik Kakdey",
	author_email="kaushik.kakdey@gmail.com",
	url="https://github.com/kakdeykaushik/python-cricket-scraper",
	project_urls={
        "Bug Tracker": "https://github.com/kakdeykaushik/python-cricket-scraper/issues",
    },
	packages = find_packages(),
	keywords= "espncricinfo cricket t20 odi test cricsheet",
	classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
		"Development Status :: 5 - Production/Stable", 
        "Operating System :: OS Independent",
    ],
	zip_safe = True
)
