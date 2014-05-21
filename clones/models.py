from django.db import models


class ClonePlate(models.Model):
    """
    A library plate of RNAi feeding clones. This plate is meant to represent
    the theoretical plate, not an individual frozen stock of the plate.
    """
    name = models.CharField(max_length=20, primary_key=True)
    screen_stage = models.PositiveSmallIntegerField(null=True, blank=True)
    number_of_wells = models.PositiveSmallIntegerField()

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        return 31 * hash(self.name)

    def __cmp__(self, other):
        # First order by screen stage
        if self.screen_stage != other.screen_stage:
            return cmp(self.screen_stage, other.screen_stage)

        # Then by name
        else:
            self_parts = self.name.split('-')
            other_parts = other.name.split('-')

            # 1st token numeric comparison
            if self_parts[0].isdigit() and other_parts[0].isdigit():
                return cmp(int(self_parts[0]), int(other_parts[0]))

            # 2nd token numeric comparison (if 1st token match)
            elif (self_parts[0] == other_parts[0]
                  and len(self_parts) > 1 and len(other_parts) > 1
                  and self_parts[1].isdigit() and other_parts[1].isdigit()):
                return cmp(int(self_parts[1]), int(other_parts[1]))

            # All other situations, simply order alphabetically
            else:
                return cmp(self.name, other.name)
