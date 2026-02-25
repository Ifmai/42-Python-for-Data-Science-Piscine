def all_thing_is_obj(object: any) -> int:
    object_dict = {
        "list": "List",
        "tuple": "Tuple",
        "set": "Set",
        "dict": "Dict",
        "str": "str"
    }
    object_type = type(object)
    object_type_name = object_dict.get(object_type.__name__, None)
    if object_type_name == str.__name__:
        print(f"{object} is in the kitchen : {object_type}")
    elif object_type_name is not None:
        print(f"{object_type_name} : {object_type}")
    else:
        print("Type not found")
    return 42
