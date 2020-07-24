import story_director as sd
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
while True:
    text = input('director > ')
    result,error = sd.run("<Input>",text)
    if error: print(f"{bcolors.WARNING}{error.as_string()}{bcolors.ENDC}")
    else: print(f"{bcolors.OKBLUE}{result}{bcolors.ENDC}")