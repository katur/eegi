class Clone:
    def __init__(self, name, plate, well):
        self.name = name
        self.plate = plate
        self.well = well

    def __eq__(self, other):
        return (self.name == other.name and self.plate == other.plate and
                self.well == other.well)

    def __hash__(self):
        return 31 * hash(self.name) * hash(self.plate) * hash(self.well)

    def __str__(self):
        return self.name + '@' + self.plate + '_' + self.well

    def __repr__(self):
        return self.__str__()

    def __cmp__(self, other):
        if self.plate == other.plate and self.well == other.well:
            if self.name < other.name:
                return -1
            elif self.name > other.name:
                return 1
            else:
                return 0
        elif self.plate == other.plate:
            assert self.well != other.well
            if self.well < other.well:
                return -1
            else:
                return 1
        else:
            assert self.plate != other.plate
            if self.plate.isdigit() and other.plate.isdigit():
                if int(self.plate) < int(other.plate):
                    return -1
                else:
                    return 1

            # if either is a string, use string comparison
            else:
                if self.plate < other.plate:
                    return -1
                else:
                    return 1
