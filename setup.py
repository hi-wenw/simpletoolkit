from setuptools import setup, find_packages

if __name__ == "__main__":
    setup(
        name='simpletoolkit',
        version='0.1.0',
        author='ShanFeng',  # 替换为你的名字
        author_email='aoei0713@gmail.com',  # 替换为你的邮箱
        description='A simple toolkit for various data processing tasks',
        packages=find_packages(),
        install_requires=[
            'esdk-obs-python==3.21.4',
            'pandas==2.0.3',
            'loguru==0.6.0'
        ],
        python_requires='>=3.8.1',  # 根据实际情况调整 Python 版本要求
    )