import os.path
import setuptools

root = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(root, 'README.md')) as f:
    long_description = f.read()
with open(os.path.join(root, 'requirements.txt')) as f:
    install_requires = [e.rstrip() for e in f.readlines()]

setuptools.setup(
    name='pydaze',
    version='0.1.0',
    url='https://github.com/mohanson/pydaze',
    license='MIT',
    author='mohanson',
    author_email='mohanson@outlook.com',
    description='Daze server by Python',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=['pydaze'],
    python_requires='>=3.6',
    install_requires=install_requires,
)
