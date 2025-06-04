import unicodedata

def aplicar_progresion(valor_inicial, incremento, operacion):
    try:
        if operacion == "suma":
            return str(float(valor_inicial) + incremento)
        elif operacion == "resta":
            return str(float(valor_inicial) - incremento)
        elif operacion == "multiplicacion":
            return str(float(valor_inicial) * incremento)
        elif operacion == "division":
            return str(float(valor_inicial) / incremento)
        else:
            return valor_inicial
    except:
        return valor_inicial

def normalizar_texto(texto):
    return ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')