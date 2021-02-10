from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name="hoodflex", 
      version="0.0.1",
      description="Python package/library that parses SEC Statements and Yahoo! stock data for financial analysis",
      author="Brian Tacderan",
      author_email="briantacderan@gmail.com",
      license="MIT",
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://github.com/briantacderan/hoodflex",
      packages=find_packages() 
      + find_packages(where="./robb_modd")
      + find_packages(where="./mobb_modd"),
      install_requires=[
          "beautifulsoup4==4.9.3",
          "DateTime==4.3",
          "ipywidgets==7.6.3",
          "matplotlib==3.3.4",
          "pandas-datareader==0.9.0"
      ],
      test_suite="nose.collector",
      tests_require=["nose"],
      include_package_data=True,
      zip_safe=False,
      classifiers=[
          "Programming Language :: Python :: 3",
          "License :: OSI Approved :: MIT License",
          "Operating System :: macOS Catalina",
      ],
      python_requires='>=3.6'
)
