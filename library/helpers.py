from library.models import LibraryWell, LibrarySequencingBlatResult

NO_BLAT = 'intended clone, no BLAT results (bad)'
NO_MATCH = 'intended clone, does not match BLAT results (bad)'
L4440_BLAT = 'L4440 with BLAT results (bad)'
L4440_NO_BLAT = 'L4440, no BLAT results (good)'
NO_CLONE_BLAT = 'no intended clone with BLAT results (bad)'
NO_CLONE_NO_BLAT = 'no intended clone, no BLAT results (good)'


def get_organized_library_wells(screen_level=None):
    '''
    Fetch all library wells, organized as:

        l[library_plate][well] = library_well

    Optionally provide a screen_level, to limit to the Primary or Secondary
    screen.

    '''
    wells = LibraryWell.objects.select_related('plate')
    if screen_level:
        wells = wells.filter(plate__screen_stage=screen_level)
    else:
        wells = wells.all()

    return organize_library_wells(wells)


def organize_library_wells(library_wells):
    '''
    Organize library_wells into:
        l[library_plate][well] = library_well

    '''
    l = {}
    for library_well in library_wells:
        plate = library_well.plate
        well = library_well.well
        if plate not in l:
            l[plate] = {}
        l[plate][well] = library_well

    return l


def get_organized_blat_results():
    '''
    Fetch all blat results, organized as:

        b[sequencing_result] = blats
    '''
    blats = (LibrarySequencingBlatResult.objects.all()
             .select_related('library_sequencing', 'clone_hit'))

    b = {}
    for blat in blats:
        seq = blat.library_sequencing
        if seq not in b:
            b[seq] = []
        b[seq].append(blat)

    return b


def categorize_sequences_by_blat_results(seqs):
    s = {
        L4440_NO_BLAT: [],
        NO_CLONE_NO_BLAT: [],
        NO_BLAT: [],
        NO_MATCH: [],
        L4440_BLAT: [],
        NO_CLONE_BLAT: [],
    }

    b = get_organized_blat_results()

    for seq in seqs:
        if seq.source_library_well:
            intended_clone = seq.source_library_well.intended_clone
        else:
            intended_clone = None

        # Handle no intended clone case
        if not intended_clone:
            if seq in b:
                s[NO_CLONE_BLAT].append(seq)
            else:
                s[NO_CLONE_NO_BLAT].append(seq)

        # Handle L4440 clone case
        elif intended_clone.is_control():
            if seq in b:
                s[L4440_BLAT].append(seq)
            else:
                s[L4440_NO_BLAT].append(seq)

        # Handle intended clone case
        else:
            if seq not in b:
                s[NO_BLAT].append(seq)
            else:
                match = get_match(b[seq], intended_clone)
                if not match:
                    s[NO_MATCH].append(seq)
                else:
                    rank = match.hit_rank
                    if rank not in s:
                        s[rank] = []
                    s[rank].append(seq)

    return s


def get_wells_to_resequence(s):
    wells_to_resequence = []

    for key in s:
        if ((isinstance(key, int) and key > 1) or
                key == NO_BLAT or key == NO_MATCH):
            wells_to_resequence.extend(
                [x.source_library_well for x in s[key]])

    return sorted(wells_to_resequence)


def get_match(blat_results, intended_clone):
    for x in blat_results:
        if x.clone_hit == intended_clone:
            return x
    return None


def avg(l):
    if l:
        return sum(l) / len(l)
    else:
        return 0


def get_avg_crl(seqs):
    return avg([x.crl for x in seqs])


def get_avg_qs(seqs):
    return avg([x.quality_score for x in seqs])


def get_number_decent_quality(seqs):
    return sum([x.is_decent_quality() for x in seqs])
