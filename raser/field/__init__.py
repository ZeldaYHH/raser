def main(args_dict):
    if len(args_dict['option']) == 0:
        print("temp")
    else:
        module_name = args_dict['option'][0]
        args_dict['option']=args_dict['option'][1:]
        try:
            module = __import__(module_name)
            module.main(args_dict)
        except ModuleNotFoundError:
            print("temp2")