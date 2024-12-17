from wxconv import WXC

def devanagari_to_wx(devanagari_text):
    wxc = WXC(order='utf2wx')
    return wxc.convert(devanagari_text)
