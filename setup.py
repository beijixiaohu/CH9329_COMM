from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ch9329Comm",
    version="1.0.9",
    author="北极小狐",
    author_email="yuhao888123@gmail.com",
    description="提供CH9329芯片的键盘/鼠标串口快捷通信方法",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=['ch9329Comm'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
