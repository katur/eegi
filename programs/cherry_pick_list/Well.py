all_rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']

all_columns = [
    '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12'
]
ten_columns = ['01', '03', '04', '05', '06', '07', '08', '09', '10', '12']
nine_columns = ['01', '03', '04', '05', '06', '08', '09', '10', '12']

all_wells = [x + y for y in all_columns for x in all_rows]
ten_wells = [x + y for y in ten_columns for x in all_rows]
nine_wells = [x + y for y in nine_columns for x in all_rows]
