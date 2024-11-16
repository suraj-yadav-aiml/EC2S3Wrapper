import setuptools

with open('./README.md','r') as file:
    package_description = file.read()

setuptools.setup(
	name = 'EC2S3Wrapper', #this should be unique
	version = '0.0.9',
	author = 'Suraj Yadav',
	author_email = 'sam124.sy@gmail.com',
	description = """
    EC2S3Wrapper is a Python package designed to simplify the management of AWS EC2 and S3 services. It provides an easy-to-use interface for common tasks like creating and managing EC2 instances, as well as uploading, downloading, and managing files in S3. Ideal for developers looking to streamline AWS operations with minimal code
    """,
	long_description = package_description,
	long_description_content_type = 'text/markdown',
	packages = setuptools.find_packages(),
	classifiers = [
	'Programming Language :: Python :: 3',
	"Operating System :: OS Independent"],
	python_requires = '>=3.10',
    install_requires=[
        'boto3'
    ]
	)