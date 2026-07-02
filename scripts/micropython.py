# micropython.py
"""
Mock del módulo 'micropython' para permitir la ejecución de const() en Python estándar.
"""

def const(x):
    """
    En MicroPython, const() es una directiva del compilador que optimiza constantes.
    En Python estándar, simplemente retorna el valor.
    """
    return x
