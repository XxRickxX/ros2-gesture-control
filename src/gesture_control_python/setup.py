from setuptools import find_packages, setup
from glob import glob# 用于安装launch文件夹下的所有launch.py文件

package_name = 'gesture_control_python'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob('launch/*.launch.py')), # 安装launch文件夹下的所有launch.py文件
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='wuh1fe',
    maintainer_email='258749898@qq.com',
    description='TODO: Package description',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'service_turtle_control = gesture_control_python.service_turtle_control:main',
            'client_turtle_control_keyboard = gesture_control_python.client_turtle_control_keyboard:main',
            'client_turtle_control_gesture = gesture_control_python.client_turtle_control_gesture:main',
        ],
    },
)
