def validate_result(result_data):
    if not result_data: return False, 'Empty Data'
    required = ['order_id', 'content', 'status']
    for k in required:
        if k not in result_data: return False, f'Missing key: {k}'
    return True, 'OK'
