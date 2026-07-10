from setuptools import setup, find_packages

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="fwfii",
    version="1.1.1",
    description="Fii Drone Flight Control SDK for F400/F600",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="fwfii",
    url="https://github.com/Kevin0412/fwfii",
    packages=find_packages(exclude=["examples", "tests"]),
    install_requires=[
        "pyserial>=3.5",
        "numpy",
        "opencv-python",
    ],
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Education",
        "Topic :: Scientific/Engineering",
    ],
    keywords="drone, flight control, education, fii, F400, F600, UAV",
)