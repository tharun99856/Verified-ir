from ir.model import Filter, GroupBy, Map, Reduce, Sort, Take

CONTRACT_VERSION = 1

_COMPLEXITY_ORDER = ["O(k)", "O(n)", "O(n log n)"]
_RANK = {complexity: rank for rank, complexity in enumerate(_COMPLEXITY_ORDER)}

_CONTRACTS = {
    Take: ("take", "O(k)"),
    Filter: ("filter", "O(n)"),
    Map: ("map", "O(n)"),
    Reduce: ("reduce", "O(n)"),
    GroupBy: ("groupby", "O(n)"),
    Sort: ("sort", "O(n log n)"),
}


def op_name(op) -> str:
    return _CONTRACTS[type(op)][0]


def op_complexity(op) -> str:
    return _CONTRACTS[type(op)][1]


def compose_complexity(ops) -> str:
    if not ops:
        return "O(1)"
    return max((op_complexity(op) for op in ops), key=lambda c: _RANK[c])


def dominant_op_names(ops):
    if not ops:
        return []
    max_rank = max(_RANK[op_complexity(op)] for op in ops)
    names = []
    for op in ops:
        if _RANK[op_complexity(op)] == max_rank:
            name = op_name(op)
            if name not in names:
                names.append(name)
    return names
