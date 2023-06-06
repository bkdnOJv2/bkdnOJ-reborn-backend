from typing import Optional, List

def parse_string_to_list_int(st: str, sep: str) -> Optional[List[int]]:
    try:
        return list(map(int, st.split(sep)))
    except:
        raise ValueError("cannot parse string to list of int")