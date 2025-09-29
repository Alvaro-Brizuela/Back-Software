import re

def validar_rut_chileno(rut: str) -> bool:
    """
    Valida un RUT chileno en formato 12345678-5 o 12.345.678-K
    """
    rut = rut.upper().replace(".", "").replace("-", "")
    if not re.match(r"^\d{7,8}[0-9K]$", rut):
        return False

    cuerpo, dv = rut[:-1], rut[-1]

    # Calcular DV
    suma = 0
    factor = 2
    for c in reversed(cuerpo):
        suma += int(c) * factor
        factor = 9 if factor == 7 else factor + 1  # ciclo 2→7
    resto = suma % 11
    dv_calculado = str(11 - resto) if resto > 1 else ("K" if resto == 1 else "0")

    return dv == dv_calculado
