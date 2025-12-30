import typing as t

JSON = t.Union[
    dict[str, "JSON"],
    list["JSON"],
    str,
    int,
    float,
    bool,
    None,
]

JSON_DICT = dict[str, JSON]
JSON_LIST = list[JSON]
