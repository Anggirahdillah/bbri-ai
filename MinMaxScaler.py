# MinMaxScaler.py
# Compatibility module supaya pickle bisa menemukan
# MinMaxScaler.MinMaxScaler dan MinMaxScaler.dtype

from sklearn.preprocessing import MinMaxScaler as _SkMinMaxScaler
import numpy as _np

# alias dtype yang dicari pickle
dtype = _np.dtype

class MinMaxScaler(_SkMinMaxScaler):
    """
    Wrapper untuk MinMaxScaler bawaan sklearn.

    Dibiarkan kosong karena kita cuma butuh nama class-nya
    supaya cocok dengan object yang sudah dipickle sebelumnya.
    """
    pass

