[app]

# (str) Title of your app
title = Neogenertex App

# (str) Package name
package.name = neogenertexapp

# (str) Package domain (needed for linux packaging)
package.domain = org.test

# (str) Source directory (directory where your app's source code is located)
source.dir = .

# (str) Version of your app
version = 1.0

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas

# (list) Source files to exclude (let empty to not exclude anything)
source.exclude_exts = spec

# (list) List of directory to exclude (let empty to not exclude anything)
source.exclude_dirs = tests, bin

# (list) List of exclusions using pattern matching
source.exclude_patterns = license,images/*/*.jpg

# (str) Path to the logo
icon.filename = %(source.dir)s/data/icon.png

# (str) Supported orientations (one of landscape, portrait or all)
orientation = portrait

# (list) List of requirements
requirements = %(source.dir)s/Pipfile

# (str) Linux distribution to use (e.g. ubuntu, debian, fedora)
linux_distribution = ubuntu

# (str) Linux package format (e.g. deb, rpm)
linux_package_format = deb