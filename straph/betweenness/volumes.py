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
    def __iadd__(self, y):
        x = self.__add__(y)
        self.val = x.val
        self.dim = x.dim
        return self
    def __mul__(self, y):
        sp = y.val
        dp = y.dim
        return Volume(self.val*sp,self.dim+dp)

    def __truediv__(self ,y):
        sp = y.val
        dp = y.dim
        return (self.val/sp,self.dim-dp)

    def __radd__(self, y):
        return self.__add__(y)

    def __str__(self):
        return "vol("+str(self.val)+","+str(self.dim)+")"
    def __repr__(self):
        return self.__str__()
