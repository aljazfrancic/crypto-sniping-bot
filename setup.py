from setuptools import setup, find_packages

setup(
    name="crypto-sniping-bot",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "web3==6.15.1",
        "python-dotenv==1.0.1",
        "eth-account==0.9.0",
        "eth-utils==2.3.1",
        "hexbytes<0.4.0,>=0.1.0",
        "websockets==11.0.3",
        "eth-typing==4.0.0",
    ],
    python_requires=">=3.8",
) 