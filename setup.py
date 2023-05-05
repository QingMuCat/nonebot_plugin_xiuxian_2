import os
import setuptools


with open("README.md", "r", encoding="utf-8", errors="ignore") as f:
    long_description = f.read()
    setuptools.setup(
    name='nonebot_plugin_xiuxian_2',
    version='2.9.2.2',
    author='QingmuCat',
    author_email='1242550160@qq.com',
    keywords=["pip", "nonebot2", "文游", "修仙"],
    url='https://github.com/QingMuCat/nonebot_plugin_xiuxian_2',
    description='''修仙插件''',
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: Chinese (Simplified)"
    ],
    include_package_data=True,
    platforms="any",
    install_requires=[
            'fastapi==0.89.1',
            'nonebot-adapter-onebot==2.2.1',
            'nonebot-plugin-apscheduler==0.2.0',
            'nonebot2==2.0.0rc3',
            'numpy==1.23.5',
            'Pillow==9.4.0',
            'urllib3==1.26.14',
            'ujson==5.7.0',
            'uvicorn==0.20.0',
            'wcwidth==0.2.6',
            'websockets==10.4',
            'wget==3.2',
            'aiohttp==3.8.4',
    ],
    )
