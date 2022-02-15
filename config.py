import os
 
env_var = input('Please enter the environment variable name:\n')
 
if env_var in os.environ:
    print(f'{env_var} value is {os.environ[env_var]}')
else:
    print(f'{env_var} does not exist')