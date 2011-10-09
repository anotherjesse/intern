#   Copyright 2011 Josh Kearney
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import setuptools

from intern import version


setuptools.setup(
    name="irc-intern",
    version=version.version_hash(),
    author="Jesse Andrews",
    author_email="anotherjesse@gmail.com",
    description="Do my work (run my script in the cloud)",
    license="Apache License, Version 2.0",
    url="http://intern.devstack.org",
    packages=["pyhole"],
    install_requires=[
        "python-novaclient",
        "pywapi"
    ],
    scripts=["bin/pyhole"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ]
)
