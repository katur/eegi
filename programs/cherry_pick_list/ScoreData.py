class ExperimentScoreData:
    def __init__(self):
        self.scores = []
        self.scorers = set()
        self.dates = set()

    def add_score(self, score):
        self.scores.append(score)

    def add_scorer(self, scorer):
        self.scorers.add(scorer)

    def add_date(self, date):
        self.dates.add(date)

    def get_collapsed_score(self):
        if not self.scores:
            raise ValueError('Scores must be non-empty')
        if 3 in self.scores:
            return 3
        elif 2 in self.scores:
            return 2
        elif 1 in self.scores:
            return 1
        elif 0 in self.scores:
            return 0
        else:
            return .5

    def __str__(self):
        return 'Scored {0}, by {1}, experiment dates: {2}'.format(
            str(self.scores), str(self.scorers), str(self.dates))

    def __repr__(self):
        return self.__str__()


class CloneScoreData:
    def __init__(self):
        self.scores = []
        self.scorers = set()
        self.dates = set()

    def add_experiment_score_data(self, other):
        self.scores.append(other.get_collapsed_score())
        for scorer in other.scorers:
            self.scorers.add(scorer)
        for date in other.dates:
            self.dates.add(date)

    def is_accepted(self, mutant):
        return mutant.accept(self.get_best_two_scores_as_string(),
                             self.scorers, self.dates)

    def get_best_two_scores_as_string(self):
        # copy the list
        scores = self.scores[:]
        if len(scores) == 0:
            scores.append(0.25)
        if len(scores) == 1:
            scores.append(0.25)
        scores = sorted(scores, reverse=True)
        scores = scores[0:2]
        assert len(scores) == 2
        assert scores[0] >= scores[1]
        for index, score in enumerate(scores):
            scores[index] = convert_to_letter(score)
        scores = ''.join(scores)
        return scores

    def __str__(self):
        return 'Scored {0}, by {1}, experiment dates: {2}'.format(
            str(self.scores), str(self.scorers), str(self.dates))

    def __repr__(self):
        return self.__str__()


def convert_to_letter(score):
    if score == 3:
        return 's'
    elif score == 2:
        return 'm'
    elif score == 1:
        return 'w'
    elif score == 0.5:
        return 'o'
    elif score == 0.25:
        return 'u'
    elif score == 0:
        return 'n'
    else:
        raise ValueError(str(score) + ' is an invalid score')
