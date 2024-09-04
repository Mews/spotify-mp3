import ast

def load_data_from_file(file_name:str):
    with open("tests/example_responses/"+file_name) as f:
        return ast.literal_eval(f.read())