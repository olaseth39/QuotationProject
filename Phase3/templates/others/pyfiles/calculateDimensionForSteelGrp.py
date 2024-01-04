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
        # Note: I previously used 1.22 but later changed to 1.2 according to Mr Dayo's directive
        # Note: I have changed back to 1.22 because that seems to be the one generally used
        values = np.round(np.arange(1.22, int(np.sqrt(self.required_volume) + 1.22), 1.22), 2)
        result = sorted(np.random.choice(values, len(values), False))

        product = []
        for i in enumerate(result[1:]):
            for count in enumerate(result[1:][i[0]:]):
                product.append('{} * {} = {}'.format(i[1], count[1], (i[1] * count[1])))

        # find the values for heights
        # maximum height possible is 3.66
        # Note: I previously used 1.22 but later changed to 1.2 according to Mr Dayo's directive
        # I have changed back to 1.22 because that seems to be the one generally used
        # I changed the maximum height to 4.88
        # Normally standard height should not be higher than 6.1 but for normalcy, I used 4.88
        val = np.arange(1.22, 4.88 + 1.22, 1.22)
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

            # choose the nearest values higher than the required_volume and within range of required_volume + 35
            # + 35 was chosen to catch enough dimension
            # It was discovered that volume 33 returned an empty list
            # So the range was changed from 10 to 11
            # It is therefore advisable to round down instead of rounding up e.g. 32.685 ~ 32 instead of 33
            # I changed it to 50 because of highers volumes up to 1 million
            elif float(v.split('=')[1]) > float(self.required_volume) and float(self.required_volume + 50) > float(
                    v.split('=')[1]):
                higher_vols.append(v)

            else:
                lower_vols.append(v)

        return higher_vols

    def calculate_dimension_grp(self):
        values = np.arange(1, int(np.sqrt(self.required_volume)) + 3, 1)
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

        # exact_vol = [v for v in vol if int(v.split('=')[1]) == int(self.required_volume)]

        # I previously used height up to 4m but was later told height of 4m is not usually feasible, so it was removed
        # I discovered that some high volumes might use fewer panels compared to smaller ones so best dimension is based
        # on number of panels to be used
        # I have changed the height to 4m as I discovered that it could give better dimension for some volumes
        for v in vol:
            # 1 was subtracted from the required_volume to start from the required volume
            # 11 was added to the required_volume to cover up to 10 values
            # It was discovered that some volumes with fractions can come up when one is deducted from the required vol
            # e.g.  49.5. For this reason I changed 1 to 0.5
            if int(v.split('=')[1]) > int(self.required_volume - 0.5) and int(self.required_volume + 11) > int(
                    v.split('=')[1]):
                higher_vols.append(v)

        return higher_vols
