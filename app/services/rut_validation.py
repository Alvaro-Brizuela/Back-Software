import re
def validar_rut_chileno(rut: str) -> bool:
    rut = rut.upper().replace(".", "").replace("-", "")
    if not re.match(r"^\d{7,8}[0-9K]$", rut):
        return False

    cuerpo, dv = rut[:-1], rut[-1]

    suma = 0
    factor = 2
    for c in reversed(cuerpo):
        suma += int(c) * factor
        factor = 2 if factor == 7 else factor + 1  # ciclo 2→7

    resto = suma % 11
    dv_calculado = (
        str(11 - resto) if resto > 1 else ("K" if resto == 1 else "0")
    )

    return dv == dv_calculado
