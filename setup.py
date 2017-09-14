from setuptools import setup, find_packages


setup(
    name='ytvbot',
    version='0.1.dev0',
    url='https://github.com/dr1s/ytvbot',
    author='drs',
    license='MIT',
    description='Download latest recordings from youtv',
    install_requires=["selenium", "pyvirtualdisplay", "psutil", "fileDownloader.py", "prettytable"],
    dependency_links = [
        "git+https://github.com/dr1s/fileDownloader.git@master#egg=fileDownloader.py-0.4.0"

    ],
    packages=find_packages(),
    include_package_data = True,
    entry_points={'console_scripts': ['ytvbot=ytvbot.bot:main']},
)
