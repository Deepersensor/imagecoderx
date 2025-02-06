"""
    Setup file for imagecoderx.
    Use setup.cfg to configure your project.

    This file was generated with PyScaffold 4.6.
    PyScaffold helps you to put up the scaffold of your new Python project.
    Learn more under: https://pyscaffold.org/
"""

from setuptools import setup, find_packages

if __name__ == "__main__":
    try:
        setup(
            use_scm_version={"version_scheme": "no-guess-dev"},
            name="imagecoderx",
            version="0.1.0",
            description="Convert images to accurate code using Tesseract and Ollama",
            author="Your Name",
            author_email="your.email@example.com",
            packages=find_packages(where="src"),
            package_dir={"": "src"},
            install_requires=[
                'ollama',
                'opencv-python',
                
                # Add other dependencies here
            ],
            entry_points={
                'console_scripts': [
                    'imagecoderx=imagecoderx.core:main',  # if you want a CLI
                ],
            },
        )
    except:  # noqa
        print(
            "\n\nAn error occurred while building the project, "
            "please ensure you have the most updated version of setuptools, "
            "setuptools_scm and wheel with:\n"
            "   pip install -U setuptools setuptools_scm wheel\n\n"
        )
        raise
