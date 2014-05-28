class Mutant:
    def __init__(self, gene, allele, temperature, accept):
        self.gene = gene
        self.allele = allele
        self.temperature = temperature
        self.accept = accept

    def __hash__(self):
        return 31 * hash(self.gene) * hash(self.allele)

    def __str__(self):
        return self.gene

    def __repr__(self):
        return self.__str__()

    def __cmp__(self, other):
        if other == 'universal':
            return 1
        elif self.gene < other.gene:
            return -1
        elif self.gene > other.gene:
            return 1
        else:
            return 0


def get_mutant(gene):
    return mutants[gene]


mutants = {
    'dhc-1':
        Mutant('dhc-1', 'or195', '25C', lambda score, scorers, dates: (
            's' in score or 'm' in score or score == 'ww' or score == 'wo')),
    'div-1':
        Mutant('div-1', 'or148', '25C', lambda score, scorers, dates: (
            's' in score or score == 'mm' or score == 'mw' or score == 'mo' or
            score == 'ww')),
    'emb-27':
        Mutant('emb-27', 'g48', '25C', lambda score, scorers, dates: (
            's' in score or 'm' in score or score == 'ww' or score == 'wo')),
    'emb-30':
        Mutant('emb-30', 'g53', '25C', lambda score, scorers, dates: (
            's' in score or score == 'mm' or score == 'mw' or score == 'mo' or
            score == 'mn' or score == 'ww' or score == 'wo')),
    'emb-8':
        Mutant('emb-8', 'hc69', '25C', lambda score, scorers, dates: (
            's' in score or score == 'mm' or score == 'mw' or score == 'mo' or
            score == 'ww')),
    'glp-1':
        Mutant('glp-1', 'or178', '22.5C', lambda score, scorers, dates: (
            score == 'ss' or score == 'sm' or score == 'sw' or score == 'so' or
            score == 'sn' or score == 'mm' or score == 'mw' or score == 'mo' or
            score == 'mn' or score == 'ww' or (
                '20100421' not in dates and (score == 'su' or score == 'mu')
            ))),
    'hcp-6':
        Mutant('hcp-6', 'mr17', '22.5C', lambda score, scorers, dates: (
            's' in score or 'm' in score or score == 'ww' or score == 'wo')),
    'lin-5':
        Mutant('lin-5', 'ev571', '25C', lambda score, scorers, dates: (
            's' in score or 'm' in score or score == 'ww' or score == 'wo')),
    'mat-1':
        Mutant('mat-1', 'ye121', '25C', lambda score, scorers, dates: (
            's' in score or score == 'mm' or score == 'mw' or score == 'mo' or
            score == 'ww')),
    'mbk-2':
        Mutant('mbk-2', 'dd5', '25C', lambda score, scorers, dates: (
            score == 'ss' or score == 'sm' or score == 'sw' or score == 'so' or
            score == 'mm' or score == 'mw' or score == 'mo' or
            score == 'ww' or (
                '20100707' not in dates and (
                    score == 'su' or score == 'sn' or score == 'mu' or
                    score == 'mn')))),
    'mel-26':
        Mutant('mel-26', 'or184', '22.5C', lambda score, scorers, dates: (
            's' in score or score == 'mm' or score == 'mw' or score == 'mo' or
            score == 'ww' or score == 'wo')),
    'par-1':
        Mutant('par-1', 'zc310', '25C', lambda score, scorers, dates: (
            's' in score or 'm' in score or score == 'ww' or score == 'wo' or (
                score == 'wu' and ('20110309' in dates or '20110330' in dates)
            ))),
    'par-2':
        Mutant('par-2', 'it5', '25C', lambda score, scorers, dates: (
            's' in score or score == 'mm' or score == 'mw' or score == 'mo' or
            score == 'ww' or score == 'wo')),
    'par-4':
        Mutant('par-4', 'it57', '22.5C', lambda score, scorers, dates: (
            's' in score or 'm' in score or score == 'ww' or score == 'wo')),
    'pod-2':
        Mutant('pod-2', 'ye60', '15C', lambda score, scorers, dates: (
            's' in score or 'm' in score or score == 'ww' or score == 'wo')),
    'rme-8':
        Mutant('rme-8', 'b1023', '20C', lambda score, scorers, dates: (
            score == 'ss' or score == 'sm' or score == 'sw' or score == 'so' or
            score == 'sn' or score == 'mm' or score == 'mw' or score == 'mo' or
            score == 'ww')),
    'spd-5':
        Mutant('spd-5', 'or213', '22.5C', lambda score, scorers, dates: (
            's' in score or 'm' in score or score == 'ww')),
    'spn-4':
        Mutant('spn-4', 'or191', '23.5C', lambda score, scorers, dates: (
            's' in score or 'm' in score or score == 'ww' or score == 'wo')),
    'tba-1':
        Mutant('tba-1', 'or346', '25C', lambda score, scorers, dates: (
            score == 'ss' or score == 'sm' or score == 'sw' or score == 'so' or
            score == 'sn' or score == 'mm' or score == 'mw' or score == 'mo' or
            score == 'mn' or (score == 'ww' and 'noah' in scorers))),
    'universal':
        'universal',
    'zen-4':
        Mutant('zen-4', 'or153', '22.5C', lambda score, scorers, dates: (
            score == 'ss' or score == 'sm' or score == 'sw' or score == 'sn' or
            score == 'mm' or score == 'mw' or score == 'mo' or (
                (score == 'so' or score == 'su') and '20100921' not in dates)
            )),
    'zyg-1':
        Mutant('zyg-1', 'b1', '22.5C', lambda score, scorers, dates: (
            's' in score or 'm' in score or score == 'ww' or score == 'wo')),
    'zyg-8':
        Mutant('zyg-8', 'b235', '25C', lambda score, scorers, dates: (
            's' in score or 'm' in score or score == 'ww' or score == 'wo')),
    'zyg-9':
        Mutant('zyg-9', 'b244', '25C', lambda score, scorers, dates: (
            's' in score or 'm' in score or score == 'ww' or score == 'wo')),
}
