table_id = 0  # keeps table names unique when using multiple indices


def get_next_table_id():
    global table_id
    table_id += 1
    return table_id


