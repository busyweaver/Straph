class Volume:
    def __init__(self, s, d):
        self.val = s
        self.dim = d
    def __eq__(self, w):
        return (self.dim == w.dim) and (self.val == w.val)
    def __add__(self, y):
        sp = y.val
        dp = y.dim
        if self.dim == dp:
            res = Volume(self.val+sp,self.dim)
        elif self.dim > dp:
            res = Volume(self.val,self.dim)
        else:
            res = Volume(sp,dp)
        return res
    def __mul__(self, y):
        sp = y.val
        dp = y.dim
        return (self.val*sp,self.dim+dp)

    def __truediv__(self ,y):
        sp = y.val
        dp = y.dim
        return (self.val/sp,self.dim-dp)
