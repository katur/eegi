from Mutant import get_mutant
from Well import ten_wells, nine_wells


class Plate:
    def __init__(self, deep_well, db_RNAiPlateID, mutant):
        self.deep_well = deep_well
        self.db_RNAiPlateID = db_RNAiPlateID
        if mutant is 'universal':
            self.db_mutant = 'universal'
            self.db_mutantAllele = 'universal'
        elif mutant is 'hybrid':
            self.db_mutant = 'hybrid'
            self.db_mutantAllele = 'hybrid'
        else:
            self.db_mutant = mutant.gene
            self.db_mutantAllele = mutant.allele

    def __str__(self):
        return self.deep_well

    def __repr__(self):
        return self.__str__()


plates = {
    'universal': Plate('universal', 'universal_F5', 'universal'),
    'tba-1 1': Plate('tba-1 1', 'or346_F6', get_mutant('tba-1')),
    'tba-1 2': Plate('tba-1 2', 'or346_F7', get_mutant('tba-1')),
    'hcp-6': Plate('hcp-6', 'mr17_F3', get_mutant('hcp-6')),
    'hybrid 1': Plate('hybrid 1', 'hybrid_F1', 'hybrid'),
    'hybrid 2': Plate('hybrid 2', 'hybrid_F2', 'hybrid'),
    'hybrid 3': Plate('hybrid 3', 'hybrid_F3', 'hybrid'),
    'hybrid 4': Plate('hybrid 4', 'hybrid_F4', 'hybrid'),
    'hybrid 5': Plate('hybrid 5', 'hybrid_F5', 'hybrid'),
    'hybrid 6': Plate('hybrid 6', 'hybrid_F6', 'hybrid'),
}


skipped_wells = {
    'universal': ['B02', 'G11'],
    'tba-1 1': ['E02', 'G07', 'G11'],
    'tba-1 2': ['H02', 'C07', 'A11'],
    'hcp-6': ['B02', 'C07', 'C11'],
    'hybrid 1': ['E02', 'D07', 'H11'],
    'hybrid 2': ['C02', 'B07', 'H11'],
    'hybrid 3': ['D02', 'D07', 'D11'],
    'hybrid 4': ['E02', 'F07', 'E11'],
    'hybrid 5': ['F02', 'H07', 'D11'],
    'hybrid 6': ['A02', 'G07', 'D11'],
}


def get_destination_plates_and_start(mutant):
    if mutant == 'universal':
        return ([plates['universal']], 'A01')
    elif mutant == get_mutant('dhc-1'):
        return ([plates['hybrid 3']], 'A01')
    elif mutant == get_mutant('div-1'):
        return ([plates['hybrid 1']], 'A01')
    elif mutant == get_mutant('emb-27'):
        return ([plates['hybrid 2']], 'A01')
    elif mutant == get_mutant('emb-30'):
        return ([plates['hybrid 3']], 'A03')
    elif mutant == get_mutant('emb-8'):
        return ([plates['hybrid 3']], 'A08')
    elif mutant == get_mutant('glp-1'):
        return ([plates['hybrid 4']], 'A01')
    elif mutant == get_mutant('hcp-6'):
        return ([plates['hcp-6']], 'A01')
    elif mutant == get_mutant('lin-5'):
        return ([plates['hybrid 4']], 'A03')
    elif mutant == get_mutant('mat-1'):
        return ([plates['hybrid 4']], 'A04')
    elif mutant == get_mutant('mbk-2'):
        return ([plates['hybrid 4']], 'A12')
    elif mutant == get_mutant('mel-26'):
        return ([plates['hybrid 5']], 'A01')
    elif mutant == get_mutant('par-1'):
        return ([plates['hybrid 5']], 'A06')
    elif mutant == get_mutant('par-2'):
        return ([plates['hybrid 5']], 'A12')
    elif mutant == get_mutant('par-4'):
        return ([plates['hybrid 6']], 'A01')
    elif mutant == get_mutant('pod-2'):
        return ([plates['hybrid 2']], 'A09')
    elif mutant == get_mutant('rme-8'):
        return ([plates['hybrid 6']], 'A03')
    elif mutant == get_mutant('spd-5'):
        return ([plates['hybrid 6']], 'A08')
    elif mutant == get_mutant('spn-4'):
        return ([plates['hybrid 6']], 'A09')
    elif mutant == get_mutant('tba-1'):
        return ([plates['tba-1 1'], plates['tba-1 2']], 'A01')
    elif mutant == get_mutant('zen-4'):
        return ([plates['hybrid 1']], 'A04')
    elif mutant == get_mutant('zyg-1'):
        return ([plates['hybrid 6']], 'A10')
    elif mutant == get_mutant('zyg-8'):
        return ([plates['hybrid 6']], 'A12')


def get_destination_wells(mutant):
    if mutant == 'universal':
        return ten_wells
    else:
        return nine_wells
