from setuptools import setup, find_packages

setup(
    name="earthscii",
    version="0.1.1",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "numpy",
        "rasterio",
    ],
    entry_points={
        "console_scripts": [
            "earthscii = earthscii.main:main_wrapper",
        ],
    },
)
