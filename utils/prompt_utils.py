import os

def get_first_system_prompt(output_format=None):
    filename = 'first_system_prompt_markdown_output.txt'
    if output_format == 'json':
        filename = 'first_system_prompt_json_output.txt'
    
    _file = open(os.path.join('data', filename), 'r', encoding='utf-8')
    system_prompt = _file.read()
    _file.close()
    
    return system_prompt
    