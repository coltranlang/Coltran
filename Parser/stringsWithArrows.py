def stringsWithArrows(text, pos_start, pos_end):
    result = ''
    error = ''
    error_at_text = ''
    if pos_start.fm_string != None:
        text = pos_start.fm_string.pos_start.fileText
        pos_start = pos_start.fm_string.pos_start
        pos_end = pos_end.fm_string.pos_end
        error_at_text = None
        
    # Calculate indices
    index_start = max(text.rfind('\n', 0, pos_start.index), 0)
    index_end = text.find('\n', index_start + 1)
    if index_end < 0: index_end = len(text)
    
    # Generate each line
    line_count = pos_end.line - pos_start.line + 1
    
    for i in range(line_count):
        # Calculate line columnumns
        line = text[index_start:index_end]
        column_start = pos_start.column if i == 0 else 0
        column_end = pos_end.column if i == line_count - 1 else len(line) - 1
        
        
        error += f"{line}"
        error += ' ' * column_start + '^' * (column_end - column_start + 1)
        error_at = error.find('^')
        if error_at_text == None:
            error_at_text = error[:error_at].split('\n')
            if len(error_at_text) > 1:
                error_at_text = error_at_text[1].strip()
            else:
                error_at_text = error_at_text[0].strip()
        if error_at_text == '':
            error_at_text = error[:error_at].strip()
        error_at_text = error_at_text.replace('\n', '')
        # Append to result
        len_error_at_text = len(error_at_text.rstrip())
        result = error_at_text + '\n     ' + '^' * len_error_at_text
    return '     ' + result


