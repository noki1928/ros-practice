from glob import glob

from setuptools import find_packages, setup

package_name = 'turtle_bringup'

setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Pavel Tsaturov',
    maintainer_email='astvacp@gmail.com',
    description='Launch the turtlesim simulator for ROS 2 practice PR02.',
    license='Apache-2.0',
    entry_points={'console_scripts': []},
)
