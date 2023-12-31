import numpy as np

"""
    Let's create a class SteelDimension that calculates the nearest possible dimensions(L, B, H) of a given volume.
    The required_volume is the given volume from which the dimension is to be calculated.
    The volumes have been divided into higher volumes and lower volumes.
    Volumes greater than the required volumes are known as higher volumes, i.e higher_vols.
    Volumes lower than the required volumes are known as lower volumes, i.e lower_vols.
    Volumes exactly the same as the required volumes are known as exact volumes, i.e exact_vols 
    For brevity, higher_vols are returned.
    In a situation where the higher_vols returned does not meet your requirement you might need to reduce the required_volume 
"""


class SteelGRPDimension():
    def __init__(self, required_volume):
        self.required_volume = required_volume

    def calculate_dimension_steel(self):
        # get values less than the square root of the required_volumes
        values = np.round(np.arange(1.22, int(np.sqrt(self.required_volume) + 1.22), 1.22), 2)
        result = sorted(np.random.choice(values, len(values), False))

        product = []
        for i in enumerate(result[1:]):
            for count in enumerate(result[1:][i[0]:]):
                product.append('{} * {} = {}'.format(i[1], count[1], (i[1] * count[1])))

        # find the values for heights
        # maximum height possible is 3.66
        val = np.arange(1.22, 3.66 + 1.22, 1.22)
        heights = sorted(np.random.choice(val, len(val), False))

        #
        vol = [f"{prod.split('=')[0]} * {height} = {np.round(float(prod.split('=')[1]) * height, 2)}"
               for height in heights for prod in product]

        # now match with the volume you are looking for
        higher_vols = []
        lower_vols = []
        for v in vol:
            if float(v.split('=')[1]) == float(self.required_volume):
                print("Volume is {}".format(v))

            # choose the nearest values higher than the required_volume and within range of required_volume + 10
            elif float(v.split('=')[1]) > float(self.required_volume) and float(self.required_volume + 10) > float(
                    v.split('=')[1]):
                higher_vols.append(v)
            else:
                lower_vols.append(v)

        return higher_vols

    def calculate_dimension_grp(self):
        values = np.arange(1, int(np.sqrt(self.required_volume)) + 2, 1)
        # print(values)
        result = sorted(np.random.choice(values, len(values), False))

        product = []
        for i in enumerate(result[1:]):
            for count in enumerate(result[1:][i[0]:]):
                product.append('{} * {} = {}'.format(i[1], count[1], (i[1] * count[1])))
                # product_2.append(np.round(i[1] * count[1], 2))

        # find the values for heights
        val = np.arange(1, 4 + 1, 1)
        heights = sorted(np.random.choice(val, len(val), False))

        vol = [f"{prod.split('=')[0]} * {height} = {int(prod.split('=')[1]) * height}" for height in heights for prod in product]

        # now match with the volume you are looking for
        higher_vols = []
        lower_vols = []

        exact_vol = [v for v in vol if int(v.split('=')[1]) == int(self.required_volume)]

        if len(exact_vol) == 0:
            for v in vol:
                # choose the nearest values higher than the required volume

                if int(v.split('=')[1]) > int(self.required_volume) and int(self.required_volume + 10) > int(v.split('=')[1]):
                    higher_vols.append(v)

            return higher_vols

        return exact_vol
