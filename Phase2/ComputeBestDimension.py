
"""
    Let's create a class BestDimension to calculate the best dimension to use
    we will calculate number of panels to be used
    The dimension with the smallest number of panels is considered as the best dimension
    The smallest number of panels gives the best price
"""


class BestDimension():
    def __init__(self, dimensions, unit, l_multiplier):
        self.dimensions = dimensions
        self.unit = unit
        self.l_multiplier = l_multiplier

    def compute_best_dimension(self):
        params = []

        # p stands for panel
        for dimension in enumerate(self.dimensions):
            l = float(dimension[1].split('=')[0].split('*')[1])
            lp = l/self.unit
            b = float(dimension[1].split('=')[0].split('*')[0])
            bp = b/self.unit
            h = float(dimension[1].split('=')[0].split('*')[2])
            hp = h/self.unit
            v = float(dimension[1].split('=')[1])

            # calculate the number of panels
            x = lp * bp * self.l_multiplier
            y = lp * hp * 2
            z = bp * hp * 2
            total = x + y + z

            params.append((l, b, h, v, int(total)))

        # best_dimension = []
        smallest_no_of_panels = min(params, key=lambda x: x[4])
        # print(smallest_no_of_panels[4])

        best_dimension = [param for param in params if param[4] == smallest_no_of_panels[4]]
        highest_length_in_best_dimension = max(best_dimension, key=lambda x: x[0])
        lowest_length_in_best_dimension = min(best_dimension,
                                              key=lambda x: x[0])  # length is always longer than breadth
        highest_width_in_best_dimension = max(best_dimension, key=lambda x: x[1])
        lowest_width_in_best_dimension = min(best_dimension, key=lambda x: x[1])
        # print(dimension)
        if len(best_dimension) > 1:
            for key, value in enumerate(best_dimension):
                print("Parameter {} is {}".format(key + 1, value))
            for dimension in best_dimension:
                if dimension[0] == lowest_length_in_best_dimension[0] and dimension[1] == \
                        lowest_width_in_best_dimension[1]:
                    result_1 = (f"To maximize space we advice you use  L={dimension[0]}, B={dimension[1]},\
                           height={dimension[2]}, Volume is {dimension[3]} and Total panels={dimension[4]}", int(f"{dimension[4]}"))

                    return result_1
        result_2 = (f"Best dimension is L={best_dimension[0][0]}, B={best_dimension[0][1]},\
               height={best_dimension[0][2]}, Volume is {best_dimension[0][3]} \
                    and Total panels={best_dimension[0][4]}", int(f"{best_dimension[0][4]}"), int(float(f"{best_dimension[0][2]}")))
        return result_2


