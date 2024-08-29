import math

# https://www.fs.usda.gov/inside-fs/delivering-mission/sustain/tree-height-diameter-relationship
# see https://www.researchgate.net/publication/341931590

# dbh : diameter at breast height in cm
# height : tree height in m
def estimate_height(dbh):
    # y = 9.9414 * ln(x) - 11.666
    height = 9.9414 * math.log(dbh) - 11.666
    return height

