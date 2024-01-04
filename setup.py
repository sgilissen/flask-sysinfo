from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
build_options = {'packages': [], 'excludes': [], 'include_files': ['templates', 'static']}

base = 'console'

executables = [
    Executable('app.py', base=base, target_name = 'Flask-SysInfo')
]

setup(name='Flask-SysInfo',
      version = '1.0',
      description = 'Simple Flask app to show system status (HDD, load, etc) on a webpage',
      options = {'build_exe': build_options},
      executables = executables)
