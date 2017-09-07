from setuptools import setup, find_packages


setup(
    name='ytvbot',
    version='0.1',
    url='https://github.com/dr1s',
    author='drs',
    license='MIT',
    description='Download latest recordings from youtv',
    install_requires=["selenium", "pyvirtualdisplay", "fileDownloader.py", "psutil"],
    packages=find_packages(),
    include_package_data = True,
    entry_points={'console_scripts': ['ytvbot=ytvbot.bot:main']},
)
