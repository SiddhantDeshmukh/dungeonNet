import matplotlib.colors as colors
import matplotlib as mpl

def tabcmapper(i: int, cmap=mpl.colormaps["tab20"], mod=19):
    # Returns the i mod-(n-1)th color from cmap, only use with qualitative
    # color maps
    return colors.rgb2hex(cmap(i % mod), keep_alpha=True)
